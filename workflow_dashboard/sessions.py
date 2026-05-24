"""Parse ~/.claude/projects/<slug>/*.jsonl session logs (read-only, fail-safe)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class Session:
    id_short: str
    title: str | None
    branch: str | None
    last_activity: str | None  # ISO string as found in log
    live: bool
    pr: int | None


def _parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def parse_session_file(path: Path, *, now: datetime, freshness_minutes: int) -> Session:
    id_short = path.stem[:8]
    title = branch = last_activity = None
    last_dt: datetime | None = None
    pr: int | None = None

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return Session(id_short, None, None, None, False, None)

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("aiTitle"):
            title = d["aiTitle"]
        if d.get("gitBranch"):
            branch = d["gitBranch"]
        if d.get("prNumber") is not None:
            pr = d["prNumber"]
        ts = d.get("timestamp")
        if ts:
            dt = _parse_ts(ts)
            if dt is not None:
                last_activity = ts
                last_dt = dt

    live = bool(last_dt and (now - last_dt) <= timedelta(minutes=freshness_minutes))
    return Session(id_short, title, branch, last_activity, live, pr)


def parse_sessions(jsonl_dir: Path, *, now: datetime, freshness_minutes: int, recent_days: int) -> list[Session]:
    if not jsonl_dir.is_dir():
        return []
    cutoff = now - timedelta(days=recent_days)
    sessions: list[Session] = []
    for path in jsonl_dir.glob("*.jsonl"):
        try:
            s = parse_session_file(path, now=now, freshness_minutes=freshness_minutes)
        except Exception:
            continue
        dt = _parse_ts(s.last_activity) if s.last_activity else None
        if dt is None or dt < cutoff:
            continue
        sessions.append(s)
    sessions.sort(key=lambda s: s.last_activity or "", reverse=True)
    return sessions
