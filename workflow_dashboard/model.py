"""Assemble the dashboard model dict from all read-only sources."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import DashboardConfig, slug_for
from .coordination import parse_coordination
from .sessions import parse_sessions
from .gitinfo import collect_git_info
from .rules import detect_conflicts


def resolve_jsonl_dir(cfg: DashboardConfig) -> Path | None:
    """Find the ~/.claude/projects/<slug> dir; fall back to a cwd scan."""
    direct = cfg.claude_projects_dir / slug_for(cfg.project_path)
    if direct.is_dir():
        return direct
    # Fallback: scan for a project dir whose name references this project_path.
    if not cfg.claude_projects_dir.is_dir():
        return None
    target = str(cfg.project_path).lower().replace("\\", "-").replace("/", "-")
    for child in cfg.claude_projects_dir.iterdir():
        if child.is_dir() and target in child.name.lower():
            return child
    return None


def build_model(cfg: DashboardConfig, *, now: datetime | None = None, runner=None) -> dict:
    now = now or datetime.now(timezone.utc)

    slots = parse_coordination(cfg.project_path / ".claude" / "coordination")

    jsonl_dir = resolve_jsonl_dir(cfg)
    sessions = (
        parse_sessions(
            jsonl_dir,
            now=now,
            freshness_minutes=cfg.freshness_minutes,
            recent_days=cfg.recent_days,
        )
        if jsonl_dir
        else []
    )

    git = collect_git_info(cfg.project_path, runner=runner, window_hours=cfg.commits_window_hours)

    conflicts = detect_conflicts(
        slots,
        sessions,
        git,
        now=now,
        freshness_minutes=cfg.freshness_minutes,
        stale_days=cfg.stale_days,
    )

    return {
        "generated_at": now.isoformat(),
        "config": {
            "freshness_minutes": cfg.freshness_minutes,
            "stale_days": cfg.stale_days,
            "recent_days": cfg.recent_days,
        },
        "projects": [
            {
                "name": cfg.project_name,
                "path": str(cfg.project_path),
                "git": asdict(git),
                "slots": [asdict(s) for s in slots],
                "sessions": [asdict(s) for s in sessions],
                "conflicts": [asdict(c) for c in conflicts],
            }
        ],
    }
