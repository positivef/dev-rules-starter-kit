from datetime import datetime, timezone

from workflow_dashboard.rules import detect_conflicts
from workflow_dashboard.coordination import Slot
from workflow_dashboard.sessions import Session
from workflow_dashboard.gitinfo import GitInfo

NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def _session(ids, branch, live):
    return Session(ids, "t", branch, "2026-05-24T15:58:00.000Z", live, None)


def _slot(name, status, last_updated):
    return Slot(name, "topic", status, last_updated, None)


CLEAN_GIT = GitInfo("main", 0, 0, 0, ["main"])


def test_slot_collision_when_two_live_sessions():
    sessions = [_session("aaaa", "main", True), _session("bbbb", "main", True)]
    out = detect_conflicts([], sessions, CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert "slot_collision" in rules
    assert rules["slot_collision"].severity == "red"


def test_no_collision_with_single_live_session():
    sessions = [_session("aaaa", "main", True), _session("bbbb", "main", False)]
    out = detect_conflicts([], sessions, CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    assert "slot_collision" not in {c.rule for c in out}


def test_branch_divergence_across_live_sessions():
    sessions = [_session("aaaa", "main", True), _session("bbbb", "feature", True)]
    out = detect_conflicts([], sessions, CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["branch_divergence"].severity == "warn"


def test_duplicate_work_two_in_progress_slots():
    slots = [
        _slot("claude-1", "in-progress", "2026-05-24T15:00:00+00:00"),
        _slot("claude-2", "in-progress", "2026-05-24T15:00:00+00:00"),
    ]
    out = detect_conflicts(slots, [], CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["duplicate_work"].severity == "warn"


def test_stale_slot_old_active_occupancy():
    slots = [_slot("claude-1", "paused", "2026-05-10T00:00:00+00:00")]
    out = detect_conflicts(slots, [], CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["stale_slot"].severity == "yellow"
    assert "claude-1" in rules["stale_slot"].detail


def test_idle_slot_never_stale():
    slots = [_slot("claude-1", "idle", "2026-01-01T00:00:00+00:00")]
    out = detect_conflicts(slots, [], CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    assert "stale_slot" not in {c.rule for c in out}


def test_uncommitted_drift():
    git = GitInfo("main", 4, 1, 0, ["main"])
    out = detect_conflicts([], [], git, now=NOW, freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["uncommitted_drift"].severity == "yellow"


def test_clean_state_no_conflicts():
    out = detect_conflicts(
        [_slot("claude-1", "idle", "2026-05-24T15:00:00+00:00")],
        [_session("aaaa", "main", True)],
        CLEAN_GIT,
        now=NOW,
        freshness_minutes=30,
        stale_days=3,
    )
    assert out == []
