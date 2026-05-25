"""Parse .claude/coordination/claude-*.md slot files (read-only, fail-safe)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SKIP = {"_template.md", "README.md"}


@dataclass
class Slot:
    slot: str
    topic: str | None
    status: str  # "in-progress" | "paused" | "idle"
    last_updated: str  # ISO 8601
    note: str | None


def _active_section(text: str) -> str:
    """Return the text of the '활성 점유' section (up to the next '## ' header)."""
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if line.startswith("## "):
            if "활성 점유" in line:
                capturing = True
                continue
            if capturing:
                break
        if capturing:
            out.append(line)
    return "\n".join(out)


def parse_slot_file(path: Path) -> Slot:
    slot = path.stem
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return Slot(slot, None, "idle", mtime, None)

    section = _active_section(text)
    heading = re.search(r"^###\s+(.+?)\s*$", section, re.MULTILINE)
    if "(없음)" in section or heading is None:
        return Slot(slot, None, "idle", mtime, None)

    # Strip a trailing done-marker (U+2705) without embedding a raw emoji (P10).
    done_marker = chr(0x2705)
    topic = heading.group(1).strip().rstrip(done_marker + " ").strip()
    status = "in-progress"
    status_line = re.search(r"^-\s*상태:\s*(.+)$", section, re.MULTILINE)
    if status_line and "paused" in status_line.group(1).lower():
        status = "paused"

    note = None
    note_line = re.search(r"^-\s*다음:\s*(.+)$", section, re.MULTILINE)
    if note_line:
        note = note_line.group(1).strip()

    return Slot(slot, topic, status, mtime, note)


def parse_coordination(coord_dir: Path) -> list[Slot]:
    if not coord_dir.is_dir():
        return []
    slots: list[Slot] = []
    for path in sorted(coord_dir.glob("*.md")):
        if path.name in SKIP:
            continue
        try:
            slots.append(parse_slot_file(path))
        except Exception:
            continue
    return slots
