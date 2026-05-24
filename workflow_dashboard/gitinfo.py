"""Collect git state for a project (read-only, fail-safe, injectable runner)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

Runner = Callable[[list, Path], str]


@dataclass
class GitInfo:
    branch: str | None
    uncommitted: int
    unpushed: int
    commits_24h: int
    worktrees: list = field(default_factory=list)


def _default_runner(args: list, cwd: Path) -> str:
    proc = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=15,
    )
    return proc.stdout


def _int(text: str, default: int = 0) -> int:
    text = (text or "").strip()
    try:
        return int(text)
    except (TypeError, ValueError):
        return default


def _parse_worktree_branches(text: str) -> list:
    branches = []
    for line in (text or "").splitlines():
        if line.startswith("branch "):
            branches.append(line.split("refs/heads/")[-1].strip())
    return branches


def collect_git_info(project_path: Path, *, runner: Runner | None = None, window_hours: int = 24) -> GitInfo:
    run = runner or _default_runner
    try:
        branch = (run(["rev-parse", "--abbrev-ref", "HEAD"], project_path) or "").strip() or None
        status = run(["status", "--porcelain"], project_path)
        uncommitted = len([line for line in (status or "").splitlines() if line.strip()])
        unpushed = _int(run(["rev-list", "--count", "@{u}..HEAD"], project_path))
        log = run(["log", f"--since={window_hours} hours ago", "--oneline"], project_path)
        commits_24h = len([line for line in (log or "").splitlines() if line.strip()])
        worktrees = _parse_worktree_branches(run(["worktree", "list", "--porcelain"], project_path))
    except Exception:
        return GitInfo(branch=None, uncommitted=0, unpushed=0, commits_24h=0, worktrees=[])
    return GitInfo(branch, uncommitted, unpushed, commits_24h, worktrees)
