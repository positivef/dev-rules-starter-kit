import json
from datetime import datetime, timezone

from workflow_dashboard.build import build_outputs
from workflow_dashboard.config import DashboardConfig

NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def test_build_outputs_writes_files(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".claude" / "coordination").mkdir(parents=True)
    cfg = DashboardConfig(
        project_path=proj,
        project_name="proj",
        claude_projects_dir=tmp_path / "home",
    )
    out = tmp_path / "out"
    fake_git = lambda args, cwd: {"rev-parse": "main"}.get(args[0], "")  # noqa: E731

    model_path, html_path = build_outputs(cfg, out_dir=out, now=NOW, runner=fake_git)

    assert model_path.exists() and html_path.exists()
    data = json.loads(model_path.read_text(encoding="utf-8"))
    assert data["projects"][0]["name"] == "proj"
    assert "<!DOCTYPE html>" in html_path.read_text(encoding="utf-8")
