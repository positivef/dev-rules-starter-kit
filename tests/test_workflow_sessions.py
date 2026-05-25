import json
from datetime import datetime, timezone
from pathlib import Path

from workflow_dashboard.sessions import parse_session_file, parse_sessions


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def test_parse_session_file_extracts_latest_fields(tmp_path):
    f = tmp_path / "8880af0b-72c6-409c-81d1-74a4be75b2c8.jsonl"
    _write_jsonl(
        f,
        [
            {
                "type": "attachment",
                "cwd": "C:/proj",
                "gitBranch": "main",
                "timestamp": "2026-05-24T15:00:00.000Z",
            },
            {"type": "ai-title", "aiTitle": "old title"},
            {"type": "ai-title", "aiTitle": "Continue fieldsync-pro development"},
            {"type": "pr-link", "prNumber": 13, "timestamp": "2026-05-24T15:30:00.000Z"},
            {
                "type": "assistant",
                "gitBranch": "worktree-vendors-p1-fix",
                "timestamp": "2026-05-24T15:57:00.000Z",
            },
        ],
    )
    s = parse_session_file(f, now=NOW, freshness_minutes=30)
    assert s.id_short == "8880af0b"
    assert s.title == "Continue fieldsync-pro development"
    assert s.branch == "worktree-vendors-p1-fix"
    assert s.pr == 13
    assert s.last_activity == "2026-05-24T15:57:00.000Z"
    assert s.live is True  # 3 minutes before NOW


def test_parse_session_file_not_live_when_old(tmp_path):
    f = tmp_path / "deadbeef-0000-0000-0000-000000000000.jsonl"
    _write_jsonl(
        f,
        [
            {
                "type": "assistant",
                "gitBranch": "main",
                "timestamp": "2026-05-24T10:00:00.000Z",
            }
        ],
    )
    s = parse_session_file(f, now=NOW, freshness_minutes=30)
    assert s.live is False


def test_parse_session_file_tolerates_bad_lines(tmp_path):
    f = tmp_path / "abcd1234-0000-0000-0000-000000000000.jsonl"
    f.write_text(
        'not json\n{"type":"assistant","timestamp":"2026-05-24T15:59:00.000Z"}\n',
        encoding="utf-8",
    )
    s = parse_session_file(f, now=NOW, freshness_minutes=30)
    assert s.last_activity == "2026-05-24T15:59:00.000Z"


def test_parse_sessions_drops_stale_beyond_recent_days(tmp_path):
    live = tmp_path / "11111111-0000-0000-0000-000000000000.jsonl"
    _write_jsonl(live, [{"type": "assistant", "timestamp": "2026-05-24T15:50:00.000Z"}])
    old = tmp_path / "22222222-0000-0000-0000-000000000000.jsonl"
    _write_jsonl(old, [{"type": "assistant", "timestamp": "2026-05-01T00:00:00.000Z"}])
    sessions = parse_sessions(tmp_path, now=NOW, freshness_minutes=30, recent_days=7)
    ids = [s.id_short for s in sessions]
    assert "11111111" in ids
    assert "22222222" not in ids


def test_parse_sessions_missing_dir_returns_empty(tmp_path):
    assert parse_sessions(tmp_path / "nope", now=NOW, freshness_minutes=30, recent_days=7) == []
