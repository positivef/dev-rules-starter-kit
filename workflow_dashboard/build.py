"""CLI entry: build model.json + index.html from read-only sources.

Usage:
    python -m workflow_dashboard.build --project-path <path> --project-name <name>
    python -m workflow_dashboard.build --project-path <path> --open
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from .config import DashboardConfig
from .model import build_model
from .render import render_html

_DEFAULT_OUT = Path(__file__).resolve().parent / "output"


def build_outputs(cfg: DashboardConfig, *, out_dir: Path, now: datetime | None = None, runner=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    model = build_model(cfg, now=now, runner=runner)
    model_path = out_dir / "model.json"
    html_path = out_dir / "index.html"
    model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(render_html(model), encoding="utf-8")
    return model_path, html_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Session Workflow Dashboard (POS-92)")
    parser.add_argument("--project-path", required=True)
    parser.add_argument("--project-name", default=None)
    parser.add_argument(
        "--claude-projects-dir",
        default=str(Path.home() / ".claude" / "projects"),
    )
    parser.add_argument("--out", default=str(_DEFAULT_OUT))
    parser.add_argument("--freshness-minutes", type=int, default=30)
    parser.add_argument("--stale-days", type=int, default=3)
    parser.add_argument("--open", action="store_true", help="open the report in a browser")
    args = parser.parse_args(argv)

    project_path = Path(args.project_path).resolve()
    cfg = DashboardConfig(
        project_path=project_path,
        project_name=args.project_name or project_path.name,
        claude_projects_dir=Path(args.claude_projects_dir),
        freshness_minutes=args.freshness_minutes,
        stale_days=args.stale_days,
    )
    model_path, html_path = build_outputs(cfg, out_dir=Path(args.out))

    model = json.loads(model_path.read_text(encoding="utf-8"))
    proj = model["projects"][0]
    n_conf = len(proj["conflicts"])
    print("[OK] dashboard built")
    print(f"     project : {proj['name']} ({proj['git']['branch']})")
    print(f"     slots   : {len(proj['slots'])}")
    print(f"     sessions: {len(proj['sessions'])}")
    print(f"     conflicts: {n_conf}")
    for c in proj["conflicts"]:
        print(f"       - [{c['severity']}] {c['rule']}: {c['detail']}")
    print(f"     model   : {model_path}")
    print(f"     html    : {html_path}")
    if args.open:
        webbrowser.open(html_path.as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
