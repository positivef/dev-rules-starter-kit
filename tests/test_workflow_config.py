from pathlib import Path
from workflow_dashboard.config import slug_for, DashboardConfig


def test_slug_for_windows_path_with_underscore():
    p = Path(r"C:\Users\user\Documents\GitHub\260404_gongpro\fieldsync-pro")
    assert slug_for(p) == "C--Users-user-Documents-GitHub-260404-gongpro-fieldsync-pro"


def test_slug_for_replaces_dot():
    p = Path(r"C:\a.b\c")
    assert slug_for(p) == "C--a-b-c"


def test_config_defaults():
    cfg = DashboardConfig(
        project_path=Path(r"C:\proj"),
        project_name="proj",
        claude_projects_dir=Path(r"C:\home\.claude\projects"),
    )
    assert cfg.freshness_minutes == 30
    assert cfg.stale_days == 3
    assert cfg.commits_window_hours == 24
    assert cfg.recent_days == 7
