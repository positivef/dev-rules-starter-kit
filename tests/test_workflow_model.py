import json
from datetime import datetime, timezone

from workflow_dashboard.config import DashboardConfig
from workflow_dashboard.model import build_model

NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def _setup_project(tmp_path):
    proj = tmp_path / "fieldsync-pro"
    coord = proj / ".claude" / "coordination"
    coord.mkdir(parents=True)
    (coord / "claude-1.md").write_text(
        "# 세션 슬롯 — claude-1\n\n## 활성 점유 (현재 작업 중)\n\n" "### 벤더 P1\n- 상태: in-progress\n\n## 최근 완료\n",
        encoding="utf-8",
    )
    projects_home = tmp_path / "projects_home"
    slug_dir = projects_home / "slug"
    slug_dir.mkdir(parents=True)
    (slug_dir / "aaaaaaaa-0000-0000-0000-000000000000.jsonl").write_text(
        json.dumps(
            {
                "type": "assistant",
                "gitBranch": "main",
                "timestamp": "2026-05-24T15:58:00.000Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return proj, projects_home, slug_dir


def test_build_model_structure(tmp_path, monkeypatch):
    proj, projects_home, slug_dir = _setup_project(tmp_path)
    cfg = DashboardConfig(
        project_path=proj,
        project_name="fieldsync-pro",
        claude_projects_dir=projects_home,
    )

    # Force slug resolution to our fixture dir + stub git
    monkeypatch.setattr("workflow_dashboard.model.resolve_jsonl_dir", lambda cfg: slug_dir)
    fake_git = lambda args, cwd: {  # noqa: E731
        "rev-parse": "main",
        "status": "",
        "rev-list": "",
        "log": "",
        "worktree": "worktree x\nbranch refs/heads/main\n",
    }.get(args[0], "")

    model = build_model(cfg, now=NOW, runner=fake_git)
    assert "generated_at" in model
    assert len(model["projects"]) == 1
    p = model["projects"][0]
    assert p["name"] == "fieldsync-pro"
    assert p["git"]["branch"] == "main"
    assert p["slots"][0]["slot"] == "claude-1"
    assert p["sessions"][0]["id_short"] == "aaaaaaaa"
    # model must be JSON-serializable
    json.dumps(model, ensure_ascii=False)
