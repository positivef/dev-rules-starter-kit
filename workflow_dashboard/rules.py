"""Tangle-detection rules over parsed slots/sessions/git (pure functions)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Conflict:
    rule: str
    severity: str  # "red" | "warn" | "yellow"
    detail: str


def _parse_iso(value: str):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def detect_conflicts(slots, sessions, git, *, now: datetime, freshness_minutes: int, stale_days: int) -> list:
    conflicts: list = []
    live = [s for s in sessions if s.live]

    # 1. slot_collision: >=2 live sessions sharing one working dir
    if len(live) >= 2:
        ids = ", ".join(s.id_short for s in live)
        conflicts.append(
            Conflict(
                "slot_collision",
                "red",
                f"{len(live)} live sessions in shared dir: {ids}",
            )
        )

    # 2. branch_divergence: live sessions on differing branches
    live_branches = {s.branch for s in live if s.branch}
    diverged = len(live_branches) >= 2
    if not diverged and git and git.branch:
        diverged = any(b != git.branch for b in live_branches)
    if live_branches and diverged:
        conflicts.append(
            Conflict(
                "branch_divergence",
                "warn",
                "live sessions span branches: " + ", ".join(sorted(live_branches)),
            )
        )

    # 3. duplicate_work: >=2 slots in-progress at once
    in_progress = [s for s in slots if s.status == "in-progress"]
    if len(in_progress) >= 2:
        names = ", ".join(s.slot for s in in_progress)
        conflicts.append(
            Conflict(
                "duplicate_work",
                "warn",
                f"{len(in_progress)} slots in-progress: {names}",
            )
        )

    # 4. stale_slot: active occupancy not updated within stale_days
    threshold = now - timedelta(days=stale_days)
    for s in slots:
        if s.status not in ("in-progress", "paused"):
            continue
        dt = _parse_iso(s.last_updated)
        if dt is not None and dt < threshold:
            age_days = (now - dt).days
            conflicts.append(
                Conflict(
                    "stale_slot",
                    "yellow",
                    f"{s.slot} active but untouched {age_days}d ({s.status})",
                )
            )

    # 5. uncommitted_drift: pending git changes
    if git and (git.uncommitted > 0 or git.unpushed > 0):
        conflicts.append(
            Conflict(
                "uncommitted_drift",
                "yellow",
                f"{git.uncommitted} uncommitted, {git.unpushed} unpushed",
            )
        )

    return conflicts
