"""Agent sync utilities for file-level collaboration locks."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

AGENT_SYNC_DIR = Path(__file__).resolve().parent.parent / "dev-context"
AGENT_SYNC_STATE_FILE = AGENT_SYNC_DIR / "agent_sync_state.json"
LOCK_FILE = AGENT_SYNC_DIR / "agent_sync_state.lock"


def _default_state() -> Dict[str, List[Dict]]:
    return {"agents": [], "locks": []}


def _load_raw_state() -> Dict:
    if not AGENT_SYNC_STATE_FILE.exists():
        return _default_state()
    try:
        raw = json.loads(AGENT_SYNC_STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _default_state()

    if isinstance(raw, list):
        # Legacy format (list of agent statuses)
        return {"agents": raw, "locks": []}
    if isinstance(raw, dict):
        agents = raw.get("agents", [])
        locks = raw.get("locks", [])
        if not isinstance(agents, list):
            agents = []
        if not isinstance(locks, list):
            locks = []
        return {"agents": agents, "locks": locks}
    return _default_state()


def get_active_locks() -> List[Dict]:
    """Return a snapshot of current file locks without mutating state."""
    state = _load_raw_state()
    locks = state.get("locks", [])
    return list(locks) if isinstance(locks, list) else []


def detect_conflicts(agent_id: str, task_id: str, files: Iterable[str]) -> List[Dict]:
    """Return conflicting locks for the given agent/task/file set."""
    normalized_files = [_normalize_path(f) for f in files if f]
    if not normalized_files:
        return []
    active = get_active_locks()
    conflicts: List[Dict] = []
    for file_path, lock in _conflicting_locks(normalized_files, active):
        if lock.get("agent_id") == agent_id and lock.get("task_id") == task_id:
            continue
        conflicts.append(lock)
    return conflicts


def _atomic_write_state(state: Dict) -> None:
    AGENT_SYNC_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = AGENT_SYNC_STATE_FILE.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, AGENT_SYNC_STATE_FILE)


@contextmanager
def _locked_state():
    AGENT_SYNC_DIR.mkdir(parents=True, exist_ok=True)
    with _file_lock():
        state = _load_raw_state()
        yield state
        _atomic_write_state(state)


@contextmanager
def _file_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_FILE.open("a+")
    try:
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.write(str(os.getpid()))
            handle.flush()
            yield
        finally:
            if os.name == "nt":
                import msvcrt

                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass


def _normalize_path(path: str) -> str:
    return str(Path(path))


def acquire_lock(agent_id: str, task_id: str, files: Iterable[str]) -> bool:
    """Attempt to lock the provided files for an agent/task combination."""
    files = [_normalize_path(f) for f in files if f]
    if not files:
        return True

    timestamp = datetime.now(timezone.utc).isoformat()

    with _locked_state() as state:
        active_locks: List[Dict] = state.setdefault("locks", [])
        for file_path, lock in _conflicting_locks(files, active_locks):
            if lock["agent_id"] == agent_id and lock.get("task_id") == task_id:
                # Re-entrant acquisition is allowed
                continue
            print(f"[LOCK_CONFLICT] '{file_path}' locked by {lock['agent_id']} ({lock.get('task_id', 'unknown')})")
            return False

        for file_path in files:
            active_locks.append(
                {
                    "file": file_path,
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "locked_at": timestamp,
                }
            )
    return True


def _conflicting_locks(files: Iterable[str], active_locks: List[Dict]) -> Iterable[Tuple[str, Dict]]:
    normalized = {_normalize_path(f) for f in files}
    for lock in active_locks:
        file_path = _normalize_path(lock.get("file", ""))
        if file_path in normalized:
            yield file_path, lock


def release_lock(agent_id: str, task_id: str) -> None:
    """Release locks owned by the agent/task combination."""
    with _locked_state() as state:
        active_locks: List[Dict] = state.setdefault("locks", [])
        before = len(active_locks)
        state["locks"] = [
            lock for lock in active_locks if not (lock.get("agent_id") == agent_id and lock.get("task_id") == task_id)
        ]
        after = len(state["locks"])
        if before != after:
            print(f"[LOCK_RELEASED] {before - after} lock(s) released for {agent_id}/{task_id}")


__all__ = ["acquire_lock", "release_lock", "get_active_locks", "detect_conflicts"]
