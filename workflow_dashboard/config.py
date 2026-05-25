"""Configuration + Claude project-slug derivation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


def slug_for(project_path: Path) -> str:
    """Derive the ~/.claude/projects/<slug> directory name from a project path.

    Claude Code replaces each of ``: \\ / _ .`` with ``-``.
    """
    return re.sub(r"[:\\/_.]", "-", str(project_path))


@dataclass
class DashboardConfig:
    project_path: Path
    project_name: str
    claude_projects_dir: Path
    freshness_minutes: int = 30
    stale_days: int = 3
    commits_window_hours: int = 24
    recent_days: int = 7
