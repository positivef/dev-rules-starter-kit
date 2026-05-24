from pathlib import Path

from workflow_dashboard.coordination import parse_coordination, parse_slot_file

ACTIVE = """# 세션 슬롯 — claude-5

## 활성 점유 (현재 작업 중)

### 멀티테넌트 Phase A 실행
- 시작: 2026-05-22
- 상태: paused (체크포인트)
- 다음: A-2 RLS cutover

## 최근 완료 (참고용)
### old
"""

IN_PROGRESS = """# 세션 슬롯 — claude-1

## 활성 점유 (현재 작업 중)

### 벤더 P1 수정
- 상태: in-progress

## 최근 완료
"""

IDLE = """# 세션 슬롯 — claude-2

## 활성 점유 (현재 작업 중)

(없음)

## 최근 완료
### something done
"""


def _write(d: Path, name: str, body: str) -> Path:
    p = d / name
    p.write_text(body, encoding="utf-8")
    return p


def test_parse_paused_slot(tmp_path):
    p = _write(tmp_path, "claude-5.md", ACTIVE)
    slot = parse_slot_file(p)
    assert slot.slot == "claude-5"
    assert slot.status == "paused"
    assert slot.topic == "멀티테넌트 Phase A 실행"
    assert "A-2 RLS" in (slot.note or "")


def test_parse_in_progress_slot(tmp_path):
    p = _write(tmp_path, "claude-1.md", IN_PROGRESS)
    slot = parse_slot_file(p)
    assert slot.status == "in-progress"
    assert slot.topic == "벤더 P1 수정"


def test_parse_idle_slot(tmp_path):
    p = _write(tmp_path, "claude-2.md", IDLE)
    slot = parse_slot_file(p)
    assert slot.status == "idle"
    assert slot.topic is None


def test_parse_coordination_skips_template_and_readme(tmp_path):
    _write(tmp_path, "claude-1.md", IN_PROGRESS)
    _write(tmp_path, "_template.md", ACTIVE)
    _write(tmp_path, "README.md", ACTIVE)
    slots = parse_coordination(tmp_path)
    assert [s.slot for s in slots] == ["claude-1"]


def test_parse_coordination_missing_dir_returns_empty(tmp_path):
    assert parse_coordination(tmp_path / "nope") == []
