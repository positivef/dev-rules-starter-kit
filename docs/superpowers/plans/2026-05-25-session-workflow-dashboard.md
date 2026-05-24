# Session Workflow Dashboard (MVP / Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only, zero-dependency tool that aggregates existing multi-session data (coordination slot files, Claude session jsonl logs, git) for a single project and renders a static HTML dashboard showing slots, sessions, git state, and 5 auto-detected "tangle" conflicts.

**Architecture:** `build.py` reads four read-only sources → assembles a `model` dict → writes `output/model.json` (debug) and a **self-contained** `output/index.html` (model embedded as a JS const, so it opens via `file://` with no server and no `fetch`). All sources are read-only; output lives in a gitignored folder; every parser is fail-safe (a broken source is skipped, never crashes the build).

**Tech Stack:** Python 3 standard library only (`json`, `subprocess`, `pathlib`, `re`, `dataclasses`, `datetime`, `argparse`). HTML + vanilla JS + CSS, no build step, no external JS libs. Tests: `pytest`.

---

## Background: confirmed data formats (from live inspection 2026-05-25)

**Coordination files** — `<project>/.claude/coordination/claude-*.md` (also `antigravity.md`). Free-form markdown:
- Slot name = file stem (`claude-1`, `claude-5`, `antigravity`). Skip `_template.md`, `README.md`.
- An `## 활성 점유 (현재 작업 중)` section. If it contains `(없음)` or no `### ` heading → **idle**.
- Otherwise the first `### ` heading is the **topic**; a `- 상태:` line contains `paused` or `in-progress`.
- Last-updated = file mtime (reliable; the in-file "최종 갱신" date is optional and unstructured).

**Session logs** — `~/.claude/projects/<slug>/<sessionId>.jsonl`, one JSON object per line. The project slug for `C:\Users\user\Documents\GitHub\260404_gongpro\fieldsync-pro` is `C--Users-user-Documents-GitHub-260404-gongpro-fieldsync-pro` (each of `:`, `\`, `/`, `_`, `.` replaced by `-`). Useful line types: any line may carry `cwd`, `gitBranch`, `timestamp`; `type:"ai-title"` carries `aiTitle` (latest = current topic); `type:"pr-link"` carries `prNumber`. Per session: take the **latest** `gitBranch`/`aiTitle`/`prNumber` and the first/last `timestamp`.

**Git** — standard porcelain commands run with `cwd=project_path` (see gitinfo task).

**Correlation note (important design departure):** coordination slots (`claude-N`) and jsonl sessions (uuid `sessionId`) share **no common key**, so they cannot be merged into one row as the design's illustrative `model.json` implied. This MVP shows them as **two correlated panels** plus a shared git panel and a conflicts list. `files_touched` per session is **deferred to Phase 2** (not reliably derivable per-session); the `duplicate_work` rule therefore uses a "two slots simultaneously in-progress" heuristic rather than file-set intersection.

---

## File Structure

```
workflow_dashboard/
  __init__.py          # package marker (empty)
  config.py            # DashboardConfig dataclass + slug_for()
  coordination.py      # Slot dataclass + parse_coordination()
  sessions.py          # Session dataclass + parse_sessions() + slug dir resolution
  gitinfo.py           # GitInfo dataclass + collect_git_info(runner injectable)
  rules.py             # Conflict dataclass + detect_conflicts() (5 rules)
  model.py             # build_model() orchestration -> dict
  render.py            # render_html(model) -> str (self-contained)
  build.py             # CLI entry: main()
  output/              # GITIGNORED: model.json + index.html (created at runtime)
  README.md            # usage + rollback (Task 9)

tests/
  test_workflow_config.py
  test_workflow_coordination.py
  test_workflow_sessions.py
  test_workflow_gitinfo.py
  test_workflow_rules.py
  test_workflow_model.py
  test_workflow_render.py
  test_workflow_build.py
```

Design rationale: one responsibility per module so each gets a focused, fast unit test. `gitinfo.collect_git_info` and `model.build_model` accept an injectable `runner` so git can be tested without a real repo. `rules.detect_conflicts` is a pure function of already-parsed data → trivially testable. Console output is **ASCII-only** (P10: no emojis in `.py`); emoji/colors live only in the HTML/JS layer. Severity values in data are ASCII (`"red"|"warn"|"yellow"`).

---

### Task 0: Branch + package skeleton + gitignore

**Files:**
- Create: `workflow_dashboard/__init__.py`
- Modify: `.gitignore` (append output ignore)

- [ ] **Step 1: Create a feature branch**

Run:
```bash
git checkout -b tool/pos-92-session-workflow-dashboard
```
Expected: `Switched to a new branch 'tool/pos-92-session-workflow-dashboard'`
(Note: the repo working tree has unrelated pre-existing modified/untracked files. Only `git add` the dashboard files listed in each task — never `git add -A`.)

- [ ] **Step 2: Create the package marker**

Create `workflow_dashboard/__init__.py`:
```python
"""Session Workflow Dashboard (POS-92) - read-only multi-session aggregator."""
```

- [ ] **Step 3: Ignore generated output**

Append to `.gitignore`:
```
# Session Workflow Dashboard generated artifacts (read-only tool output)
workflow_dashboard/output/
```

- [ ] **Step 4: Verify package imports**

Run: `python -c "import workflow_dashboard; print('ok')"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/__init__.py .gitignore
git commit -m "chore(dashboard): scaffold workflow_dashboard package (POS-92)"
```

---

### Task 1: config.py — slug + config dataclass

**Files:**
- Create: `workflow_dashboard/config.py`
- Test: `tests/test_workflow_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_config.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.config'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/config.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_config.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/config.py tests/test_workflow_config.py
git commit -m "feat(dashboard): add config + claude slug derivation"
```

---

### Task 2: coordination.py — parse slot files

**Files:**
- Create: `workflow_dashboard/coordination.py`
- Test: `tests/test_workflow_coordination.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_coordination.py`:
```python
from pathlib import Path
from workflow_dashboard.coordination import parse_coordination, parse_slot_file, Slot

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_coordination.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.coordination'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/coordination.py`:
```python
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

    topic = heading.group(1).strip().rstrip("✅ ").strip()
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_coordination.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/coordination.py tests/test_workflow_coordination.py
git commit -m "feat(dashboard): parse coordination slot files"
```

---

### Task 3: sessions.py — parse jsonl session logs

**Files:**
- Create: `workflow_dashboard/sessions.py`
- Test: `tests/test_workflow_sessions.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_sessions.py`:
```python
import json
from datetime import datetime, timezone
from pathlib import Path
from workflow_dashboard.sessions import parse_session_file, parse_sessions, Session


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def test_parse_session_file_extracts_latest_fields(tmp_path):
    f = tmp_path / "8880af0b-72c6-409c-81d1-74a4be75b2c8.jsonl"
    _write_jsonl(f, [
        {"type": "attachment", "cwd": "C:/proj", "gitBranch": "main",
         "timestamp": "2026-05-24T15:00:00.000Z"},
        {"type": "ai-title", "aiTitle": "old title"},
        {"type": "ai-title", "aiTitle": "Continue fieldsync-pro development"},
        {"type": "pr-link", "prNumber": 13, "timestamp": "2026-05-24T15:30:00.000Z"},
        {"type": "assistant", "gitBranch": "worktree-vendors-p1-fix",
         "timestamp": "2026-05-24T15:57:00.000Z"},
    ])
    s = parse_session_file(f, now=NOW, freshness_minutes=30)
    assert s.id_short == "8880af0b"
    assert s.title == "Continue fieldsync-pro development"
    assert s.branch == "worktree-vendors-p1-fix"
    assert s.pr == 13
    assert s.last_activity == "2026-05-24T15:57:00.000Z"
    assert s.live is True  # 3 minutes before NOW


def test_parse_session_file_not_live_when_old(tmp_path):
    f = tmp_path / "deadbeef-0000-0000-0000-000000000000.jsonl"
    _write_jsonl(f, [
        {"type": "assistant", "gitBranch": "main",
         "timestamp": "2026-05-24T10:00:00.000Z"},
    ])
    s = parse_session_file(f, now=NOW, freshness_minutes=30)
    assert s.live is False


def test_parse_session_file_tolerates_bad_lines(tmp_path):
    f = tmp_path / "abcd1234-0000-0000-0000-000000000000.jsonl"
    f.write_text('not json\n{"type":"assistant","timestamp":"2026-05-24T15:59:00.000Z"}\n',
                 encoding="utf-8")
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
    assert parse_sessions(tmp_path / "nope", now=NOW,
                          freshness_minutes=30, recent_days=7) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_sessions.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.sessions'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/sessions.py`:
```python
"""Parse ~/.claude/projects/<slug>/*.jsonl session logs (read-only, fail-safe)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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


def parse_sessions(jsonl_dir: Path, *, now: datetime,
                   freshness_minutes: int, recent_days: int) -> list[Session]:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_sessions.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/sessions.py tests/test_workflow_sessions.py
git commit -m "feat(dashboard): parse jsonl session logs"
```

---

### Task 4: gitinfo.py — git state via injectable runner

**Files:**
- Create: `workflow_dashboard/gitinfo.py`
- Test: `tests/test_workflow_gitinfo.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_gitinfo.py`:
```python
from pathlib import Path
from workflow_dashboard.gitinfo import collect_git_info, GitInfo


def make_runner(responses):
    """responses: dict mapping the git subcommand (args[0]) to stdout str."""
    def runner(args, cwd):
        return responses.get(args[0], "")
    return runner


def test_collect_git_info_parses_all_fields():
    responses = {
        "rev-parse": "worktree-vendors-p1-fix",
        "status": " M a.py\n?? b.py\n",
        "rev-list": "2",
        "log": "aaa commit1\nbbb commit2\nccc commit3\n",
        "worktree": (
            "worktree C:/proj\nHEAD 111\nbranch refs/heads/main\n\n"
            "worktree C:/proj/.claude/worktrees/x\nHEAD 222\n"
            "branch refs/heads/feature\n"
        ),
    }
    gi = collect_git_info(Path("C:/proj"), runner=make_runner(responses),
                          window_hours=24)
    assert gi.branch == "worktree-vendors-p1-fix"
    assert gi.uncommitted == 2
    assert gi.unpushed == 2
    assert gi.commits_24h == 3
    assert gi.worktrees == ["main", "feature"]


def test_collect_git_info_failsafe_on_runner_error():
    def boom(args, cwd):
        raise RuntimeError("git not found")
    gi = collect_git_info(Path("C:/proj"), runner=boom)
    assert gi == GitInfo(branch=None, uncommitted=0, unpushed=0,
                         commits_24h=0, worktrees=[])


def test_collect_git_info_no_upstream():
    responses = {"rev-parse": "main", "status": "", "log": "",
                 "worktree": "worktree C:/proj\nbranch refs/heads/main\n"}
    # rev-list returns "" (no upstream) -> unpushed stays 0
    gi = collect_git_info(Path("C:/proj"), runner=make_runner(responses))
    assert gi.unpushed == 0
    assert gi.uncommitted == 0
    assert gi.commits_24h == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_gitinfo.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.gitinfo'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/gitinfo.py`:
```python
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
        ["git"] + args, cwd=str(cwd),
        capture_output=True, text=True, timeout=15,
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


def collect_git_info(project_path: Path, *, runner: Runner | None = None,
                     window_hours: int = 24) -> GitInfo:
    run = runner or _default_runner
    try:
        branch = (run(["rev-parse", "--abbrev-ref", "HEAD"], project_path) or "").strip() or None
        status = run(["status", "--porcelain"], project_path)
        uncommitted = len([l for l in (status or "").splitlines() if l.strip()])
        unpushed = _int(run(["rev-list", "--count", "@{u}..HEAD"], project_path))
        log = run(["log", f"--since={window_hours} hours ago", "--oneline"], project_path)
        commits_24h = len([l for l in (log or "").splitlines() if l.strip()])
        worktrees = _parse_worktree_branches(
            run(["worktree", "list", "--porcelain"], project_path)
        )
    except Exception:
        return GitInfo(branch=None, uncommitted=0, unpushed=0,
                       commits_24h=0, worktrees=[])
    return GitInfo(branch, uncommitted, unpushed, commits_24h, worktrees)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_gitinfo.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/gitinfo.py tests/test_workflow_gitinfo.py
git commit -m "feat(dashboard): collect git state with injectable runner"
```

---

### Task 5: rules.py — 5 conflict-detection rules

**Files:**
- Create: `workflow_dashboard/rules.py`
- Test: `tests/test_workflow_rules.py`

Rule definitions (all derivable from already-parsed data):
| id | severity | condition |
|---|---|---|
| `slot_collision` | red | ≥2 **live** sessions in the project (shared-dir concurrency precondition) |
| `branch_divergence` | warn | live sessions span ≥2 distinct branches, or a live session's branch ≠ git current branch |
| `duplicate_work` | warn | ≥2 coordination slots with status `in-progress` simultaneously |
| `stale_slot` | yellow | a slot with active occupancy (in-progress/paused) whose `last_updated` is older than `stale_days` |
| `uncommitted_drift` | yellow | git `uncommitted > 0` or `unpushed > 0` |

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_rules.py`:
```python
from datetime import datetime, timezone
from workflow_dashboard.rules import detect_conflicts, Conflict
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
    out = detect_conflicts([], sessions, CLEAN_GIT, now=NOW,
                           freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert "slot_collision" in rules
    assert rules["slot_collision"].severity == "red"


def test_no_collision_with_single_live_session():
    sessions = [_session("aaaa", "main", True), _session("bbbb", "main", False)]
    out = detect_conflicts([], sessions, CLEAN_GIT, now=NOW,
                           freshness_minutes=30, stale_days=3)
    assert "slot_collision" not in {c.rule for c in out}


def test_branch_divergence_across_live_sessions():
    sessions = [_session("aaaa", "main", True), _session("bbbb", "feature", True)]
    out = detect_conflicts([], sessions, CLEAN_GIT, now=NOW,
                           freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["branch_divergence"].severity == "warn"


def test_duplicate_work_two_in_progress_slots():
    slots = [_slot("claude-1", "in-progress", "2026-05-24T15:00:00+00:00"),
             _slot("claude-2", "in-progress", "2026-05-24T15:00:00+00:00")]
    out = detect_conflicts(slots, [], CLEAN_GIT, now=NOW,
                           freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["duplicate_work"].severity == "warn"


def test_stale_slot_old_active_occupancy():
    slots = [_slot("claude-1", "paused", "2026-05-10T00:00:00+00:00")]
    out = detect_conflicts(slots, [], CLEAN_GIT, now=NOW,
                           freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["stale_slot"].severity == "yellow"
    assert "claude-1" in rules["stale_slot"].detail


def test_idle_slot_never_stale():
    slots = [_slot("claude-1", "idle", "2026-01-01T00:00:00+00:00")]
    out = detect_conflicts(slots, [], CLEAN_GIT, now=NOW,
                           freshness_minutes=30, stale_days=3)
    assert "stale_slot" not in {c.rule for c in out}


def test_uncommitted_drift():
    git = GitInfo("main", 4, 1, 0, ["main"])
    out = detect_conflicts([], [], git, now=NOW,
                           freshness_minutes=30, stale_days=3)
    rules = {c.rule: c for c in out}
    assert rules["uncommitted_drift"].severity == "yellow"


def test_clean_state_no_conflicts():
    out = detect_conflicts([_slot("claude-1", "idle", "2026-05-24T15:00:00+00:00")],
                           [_session("aaaa", "main", True)],
                           CLEAN_GIT, now=NOW, freshness_minutes=30, stale_days=3)
    assert out == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_rules.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.rules'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/rules.py`:
```python
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


def detect_conflicts(slots, sessions, git, *, now: datetime,
                     freshness_minutes: int, stale_days: int) -> list:
    conflicts: list = []
    live = [s for s in sessions if s.live]

    # 1. slot_collision: >=2 live sessions sharing one working dir
    if len(live) >= 2:
        ids = ", ".join(s.id_short for s in live)
        conflicts.append(Conflict(
            "slot_collision", "red",
            f"{len(live)} live sessions in shared dir: {ids}",
        ))

    # 2. branch_divergence: live sessions on differing branches
    live_branches = {s.branch for s in live if s.branch}
    diverged = len(live_branches) >= 2
    if not diverged and git and git.branch:
        diverged = any(b != git.branch for b in live_branches)
    if live_branches and diverged:
        conflicts.append(Conflict(
            "branch_divergence", "warn",
            "live sessions span branches: " + ", ".join(sorted(live_branches)),
        ))

    # 3. duplicate_work: >=2 slots in-progress at once
    in_progress = [s for s in slots if s.status == "in-progress"]
    if len(in_progress) >= 2:
        names = ", ".join(s.slot for s in in_progress)
        conflicts.append(Conflict(
            "duplicate_work", "warn",
            f"{len(in_progress)} slots in-progress: {names}",
        ))

    # 4. stale_slot: active occupancy not updated within stale_days
    threshold = now - timedelta(days=stale_days)
    for s in slots:
        if s.status not in ("in-progress", "paused"):
            continue
        dt = _parse_iso(s.last_updated)
        if dt is not None and dt < threshold:
            age_days = (now - dt).days
            conflicts.append(Conflict(
                "stale_slot", "yellow",
                f"{s.slot} active but untouched {age_days}d ({s.status})",
            ))

    # 5. uncommitted_drift: pending git changes
    if git and (git.uncommitted > 0 or git.unpushed > 0):
        conflicts.append(Conflict(
            "uncommitted_drift", "yellow",
            f"{git.uncommitted} uncommitted, {git.unpushed} unpushed",
        ))

    return conflicts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_rules.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/rules.py tests/test_workflow_rules.py
git commit -m "feat(dashboard): add 5 tangle-detection rules"
```

---

### Task 6: model.py — assemble the model dict

**Files:**
- Create: `workflow_dashboard/model.py`
- Test: `tests/test_workflow_model.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_model.py`:
```python
import json
from datetime import datetime, timezone
from pathlib import Path
from workflow_dashboard.config import DashboardConfig
from workflow_dashboard.model import build_model

NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def _setup_project(tmp_path):
    proj = tmp_path / "fieldsync-pro"
    coord = proj / ".claude" / "coordination"
    coord.mkdir(parents=True)
    (coord / "claude-1.md").write_text(
        "# 세션 슬롯 — claude-1\n\n## 활성 점유 (현재 작업 중)\n\n"
        "### 벤더 P1\n- 상태: in-progress\n\n## 최근 완료\n",
        encoding="utf-8",
    )
    projects_home = tmp_path / "projects_home"
    slug_dir = projects_home / "slug"
    slug_dir.mkdir(parents=True)
    (slug_dir / "aaaaaaaa-0000-0000-0000-000000000000.jsonl").write_text(
        json.dumps({"type": "assistant", "gitBranch": "main",
                    "timestamp": "2026-05-24T15:58:00.000Z"}) + "\n",
        encoding="utf-8",
    )
    return proj, projects_home, slug_dir


def test_build_model_structure(tmp_path, monkeypatch):
    proj, projects_home, slug_dir = _setup_project(tmp_path)
    cfg = DashboardConfig(project_path=proj, project_name="fieldsync-pro",
                          claude_projects_dir=projects_home)

    # Force slug resolution to our fixture dir + stub git
    monkeypatch.setattr("workflow_dashboard.model.resolve_jsonl_dir",
                        lambda cfg: slug_dir)
    fake_git = lambda args, cwd: {
        "rev-parse": "main", "status": "", "rev-list": "", "log": "",
        "worktree": "worktree x\nbranch refs/heads/main\n",
    }.get(args[0], "")

    model = build_model(cfg, now=NOW, runner=fake_git)
    assert "generated_at" in model
    assert len(model["projects"]) == 1
    p = model["projects"][0]
    assert p["name"] == "fieldsync-pro"
    assert p["git"]["branch"] == "main"
    assert p["slots"][0]["slot"] == "claude-1"
    assert p["sessions"][0]["id_short"] == "aaaaaaaa"
    # model must be JSON-serializable
    json.dumps(model, ensure_ascii=False)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.model'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/model.py`:
```python
"""Assemble the dashboard model dict from all read-only sources."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import DashboardConfig, slug_for
from .coordination import parse_coordination
from .sessions import parse_sessions
from .gitinfo import collect_git_info
from .rules import detect_conflicts


def resolve_jsonl_dir(cfg: DashboardConfig) -> Path | None:
    """Find the ~/.claude/projects/<slug> dir; fall back to a cwd scan."""
    direct = cfg.claude_projects_dir / slug_for(cfg.project_path)
    if direct.is_dir():
        return direct
    # Fallback: scan for a project dir whose logs reference this project_path.
    if not cfg.claude_projects_dir.is_dir():
        return None
    target = str(cfg.project_path).lower()
    for child in cfg.claude_projects_dir.iterdir():
        if child.is_dir() and target.replace("\\", "-").replace("/", "-") in child.name.lower():
            return child
    return None


def build_model(cfg: DashboardConfig, *, now: datetime | None = None,
                runner=None) -> dict:
    now = now or datetime.now(timezone.utc)

    slots = parse_coordination(cfg.project_path / ".claude" / "coordination")

    jsonl_dir = resolve_jsonl_dir(cfg)
    sessions = (parse_sessions(jsonl_dir, now=now,
                               freshness_minutes=cfg.freshness_minutes,
                               recent_days=cfg.recent_days)
                if jsonl_dir else [])

    git = collect_git_info(cfg.project_path, runner=runner,
                           window_hours=cfg.commits_window_hours)

    conflicts = detect_conflicts(slots, sessions, git, now=now,
                                 freshness_minutes=cfg.freshness_minutes,
                                 stale_days=cfg.stale_days)

    return {
        "generated_at": now.isoformat(),
        "config": {
            "freshness_minutes": cfg.freshness_minutes,
            "stale_days": cfg.stale_days,
            "recent_days": cfg.recent_days,
        },
        "projects": [{
            "name": cfg.project_name,
            "path": str(cfg.project_path),
            "git": asdict(git),
            "slots": [asdict(s) for s in slots],
            "sessions": [asdict(s) for s in sessions],
            "conflicts": [asdict(c) for c in conflicts],
        }],
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_model.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/model.py tests/test_workflow_model.py
git commit -m "feat(dashboard): assemble model from all sources"
```

---

### Task 7: render.py — self-contained HTML

**Files:**
- Create: `workflow_dashboard/render.py`
- Test: `tests/test_workflow_render.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_render.py`:
```python
from workflow_dashboard.render import render_html


def _model():
    return {
        "generated_at": "2026-05-24T16:00:00+00:00",
        "config": {"freshness_minutes": 30, "stale_days": 3, "recent_days": 7},
        "projects": [{
            "name": "fieldsync-pro",
            "path": "C:/proj",
            "git": {"branch": "main", "uncommitted": 4, "unpushed": 0,
                    "commits_24h": 2, "worktrees": ["main"]},
            "slots": [{"slot": "claude-1", "topic": "벤더 P1",
                       "status": "in-progress",
                       "last_updated": "2026-05-24T15:00:00+00:00", "note": None}],
            "sessions": [{"id_short": "aaaaaaaa", "title": "dev",
                          "branch": "main",
                          "last_activity": "2026-05-24T15:58:00.000Z",
                          "live": True, "pr": 13}],
            "conflicts": [{"rule": "uncommitted_drift", "severity": "yellow",
                           "detail": "4 uncommitted, 0 unpushed"}],
        }],
    }


def test_render_html_is_self_contained():
    html = render_html(_model())
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert "const MODEL" in html
    assert "fieldsync-pro" in html
    # Korean topic preserved (UTF-8, not escaped to ascii)
    assert "벤더 P1" in html
    # no external network deps
    assert "http://" not in html and "https://" not in html


def test_render_html_escapes_script_close_in_data():
    model = _model()
    model["projects"][0]["slots"][0]["topic"] = "danger </script><script>x"
    html = render_html(model)
    # the literal closing tag from data must not appear unescaped
    assert "</script><script>x" not in html
    assert "<\\/script>" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.render'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/render.py`:
```python
"""Render the model dict into a single self-contained HTML file."""
from __future__ import annotations

import json

_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session Workflow Dashboard</title>
<style>
:root{color-scheme:dark}
body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;
background:#0d1117;color:#e6edf3;padding:24px}
h1{font-size:20px;margin:0 0 4px}
.meta{color:#8b949e;font-size:12px;margin-bottom:20px}
.project{border:1px solid #30363d;border-radius:10px;padding:16px;margin-bottom:20px}
.project h2{margin:0 0 8px;font-size:16px}
.git{font-size:13px;color:#8b949e;margin-bottom:12px}
.git b{color:#e6edf3}
table{width:100%;border-collapse:collapse;margin:8px 0 16px;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #21262d}
th{color:#8b949e;font-weight:600}
.live{color:#3fb950;font-weight:600}
.badge{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px}
.in-progress{background:#1f6feb33;color:#79c0ff}
.paused{background:#9e6a0322;color:#e3b341}
.idle{background:#30363d;color:#8b949e}
.conflicts{margin:0 0 8px}
.c{padding:8px 12px;border-radius:8px;margin:6px 0;font-size:13px}
.c.red{background:#da363322;border:1px solid #da3633}
.c.warn{background:#9e6a0322;border:1px solid #bb8009}
.c.yellow{background:#9e6a0314;border:1px solid #54600c}
.none{color:#3fb950;font-size:13px}
.section-label{font-size:12px;color:#8b949e;text-transform:uppercase;
letter-spacing:.5px;margin-top:8px}
</style>
</head>
<body>
<h1>Session Workflow Dashboard</h1>
<div class="meta" id="meta"></div>
<div id="root"></div>
<script>
const MODEL = __MODEL__;
const SEV = {red:"\\u{1F534}", warn:"\\u26A0\\uFE0F", yellow:"\\u{1F7E1}"};
function esc(s){return (s==null?"":String(s)).replace(/[&<>]/g,
  c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}
function render(){
  const m=MODEL;
  document.getElementById("meta").textContent=
    "generated "+m.generated_at+"  |  freshness "+m.config.freshness_minutes+
    "min, stale "+m.config.stale_days+"d";
  const root=document.getElementById("root");
  root.innerHTML=m.projects.map(p=>{
    const conflicts = p.conflicts.length
      ? p.conflicts.map(c=>`<div class="c ${esc(c.severity)}">`+
          `${SEV[c.severity]||""} <b>${esc(c.rule)}</b> — ${esc(c.detail)}</div>`).join("")
      : `<div class="none">\\u2705 no tangles detected</div>`;
    const slots = p.slots.map(s=>`<tr>`+
      `<td>${esc(s.slot)}</td>`+
      `<td><span class="badge ${esc(s.status)}">${esc(s.status)}</span></td>`+
      `<td>${esc(s.topic)||"<i>—</i>"}</td>`+
      `<td>${esc((s.last_updated||"").slice(0,16))}</td></tr>`).join("");
    const sessions = p.sessions.map(s=>`<tr>`+
      `<td>${esc(s.id_short)}</td>`+
      `<td>${s.live?'<span class="live">live</span>':""}</td>`+
      `<td>${esc(s.title)||"<i>—</i>"}</td>`+
      `<td>${esc(s.branch)||"<i>—</i>"}</td>`+
      `<td>${esc((s.last_activity||"").slice(0,16))}</td>`+
      `<td>${s.pr?("#"+esc(s.pr)):""}</td></tr>`).join("");
    const g=p.git;
    return `<div class="project">
      <h2>${esc(p.name)}</h2>
      <div class="git">branch <b>${esc(g.branch)}</b> &middot;
        <b>${g.uncommitted}</b> uncommitted &middot;
        <b>${g.unpushed}</b> unpushed &middot;
        <b>${g.commits_24h}</b> commits/24h &middot;
        worktrees: ${esc((g.worktrees||[]).join(", "))||"—"}</div>
      <div class="conflicts">${conflicts}</div>
      <div class="section-label">Slots (coordination)</div>
      <table><tr><th>slot</th><th>status</th><th>topic</th><th>updated</th></tr>
        ${slots||'<tr><td colspan=4><i>none</i></td></tr>'}</table>
      <div class="section-label">Sessions (recent)</div>
      <table><tr><th>id</th><th></th><th>title</th><th>branch</th>
        <th>last activity</th><th>pr</th></tr>
        ${sessions||'<tr><td colspan=6><i>none</i></td></tr>'}</table>
    </div>`;
  }).join("");
}
render();
</script>
</body>
</html>
"""


def render_html(model: dict) -> str:
    data = json.dumps(model, ensure_ascii=False).replace("</", "<\\/")
    return _TEMPLATE.replace("__MODEL__", data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_render.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/render.py tests/test_workflow_render.py
git commit -m "feat(dashboard): render self-contained HTML view"
```

---

### Task 8: build.py — CLI entry + real smoke run

**Files:**
- Create: `workflow_dashboard/build.py`
- Test: `tests/test_workflow_build.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_workflow_build.py`:
```python
import json
from pathlib import Path
from workflow_dashboard.build import build_outputs
from workflow_dashboard.config import DashboardConfig
from datetime import datetime, timezone

NOW = datetime(2026, 5, 24, 16, 0, 0, tzinfo=timezone.utc)


def test_build_outputs_writes_files(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".claude" / "coordination").mkdir(parents=True)
    cfg = DashboardConfig(project_path=proj, project_name="proj",
                          claude_projects_dir=tmp_path / "home")
    out = tmp_path / "out"
    fake_git = lambda args, cwd: {"rev-parse": "main"}.get(args[0], "")

    model_path, html_path = build_outputs(cfg, out_dir=out, now=NOW, runner=fake_git)

    assert model_path.exists() and html_path.exists()
    data = json.loads(model_path.read_text(encoding="utf-8"))
    assert data["projects"][0]["name"] == "proj"
    assert "<!DOCTYPE html>" in html_path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow_build.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'workflow_dashboard.build'`

- [ ] **Step 3: Write minimal implementation**

Create `workflow_dashboard/build.py`:
```python
"""CLI entry: build model.json + index.html from read-only sources.

Usage:
    python -m workflow_dashboard.build --project-path <path> --project-name <name>
    python -m workflow_dashboard.build --project-path <path> --open
"""
from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from .config import DashboardConfig
from .model import build_model
from .render import render_html

_DEFAULT_OUT = Path(__file__).resolve().parent / "output"


def build_outputs(cfg: DashboardConfig, *, out_dir: Path,
                  now: datetime | None = None, runner=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    model = build_model(cfg, now=now, runner=runner)
    model_path = out_dir / "model.json"
    html_path = out_dir / "index.html"
    model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    html_path.write_text(render_html(model), encoding="utf-8")
    return model_path, html_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Session Workflow Dashboard (POS-92)")
    parser.add_argument("--project-path", required=True)
    parser.add_argument("--project-name", default=None)
    parser.add_argument("--claude-projects-dir",
                        default=str(Path.home() / ".claude" / "projects"))
    parser.add_argument("--out", default=str(_DEFAULT_OUT))
    parser.add_argument("--freshness-minutes", type=int, default=30)
    parser.add_argument("--stale-days", type=int, default=3)
    parser.add_argument("--open", action="store_true", help="open the report in a browser")
    args = parser.parse_args(argv)

    project_path = Path(args.project_path).resolve()
    cfg = DashboardConfig(
        project_path=project_path,
        project_name=args.project_name or project_path.name,
        claude_projects_dir=Path(args.claude_projects_dir),
        freshness_minutes=args.freshness_minutes,
        stale_days=args.stale_days,
    )
    model_path, html_path = build_outputs(cfg, out_dir=Path(args.out))

    model = json.loads(model_path.read_text(encoding="utf-8"))
    proj = model["projects"][0]
    n_conf = len(proj["conflicts"])
    print("[OK] dashboard built")
    print(f"     project : {proj['name']} ({proj['git']['branch']})")
    print(f"     slots   : {len(proj['slots'])}")
    print(f"     sessions: {len(proj['sessions'])}")
    print(f"     conflicts: {n_conf}")
    for c in proj["conflicts"]:
        print(f"       - [{c['severity']}] {c['rule']}: {c['detail']}")
    print(f"     model   : {model_path}")
    print(f"     html    : {html_path}")
    if args.open:
        webbrowser.open(html_path.as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow_build.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Run the FULL suite + a real smoke run**

Run: `pytest tests/test_workflow_*.py -v`
Expected: PASS (all workflow tests green)

Run (real data, fieldsync-pro):
```bash
python -m workflow_dashboard.build --project-path "C:/Users/user/Documents/GitHub/260404_gongpro/fieldsync-pro" --project-name fieldsync-pro
```
Expected: `[OK] dashboard built` with non-empty slots, sessions, and at least the `slot_collision` (two live sessions) + `uncommitted_drift` conflicts. Open `workflow_dashboard/output/index.html` in a browser and confirm the project card, slot table, session table (live rows highlighted), and conflict banner render.

- [ ] **Step 6: Commit**

```bash
git add workflow_dashboard/build.py tests/test_workflow_build.py
git commit -m "feat(dashboard): add build CLI + verify against real data (POS-92)"
```

---

### Task 9: README + ruff + final verification

**Files:**
- Create: `workflow_dashboard/README.md`

- [ ] **Step 1: Write the README**

Create `workflow_dashboard/README.md`:
```markdown
# Session Workflow Dashboard (POS-92, MVP / Phase 1)

Read-only aggregator that surfaces multi-session "tangles" for one project.

## Run
```bash
python -m workflow_dashboard.build \
  --project-path "C:/Users/user/Documents/GitHub/260404_gongpro/fieldsync-pro" \
  --project-name fieldsync-pro --open
```
Output: `workflow_dashboard/output/{model.json,index.html}` (gitignored).
The HTML is self-contained — open it directly, no server needed.

## What it shows
- **Slots** from `.claude/coordination/claude-*.md` (slot, status, topic, updated)
- **Sessions** from `~/.claude/projects/<slug>/*.jsonl` (id, live?, title, branch, PR)
- **Git** state of the project (branch, uncommitted, unpushed, commits/24h, worktrees)
- **Conflicts** (5 rules): slot_collision, branch_divergence, duplicate_work,
  stale_slot, uncommitted_drift

## Safety
Read-only (writes nothing to sources), idempotent, fail-safe (a broken source is
skipped). Rollback = delete `workflow_dashboard/output/` then `workflow_dashboard/`
(zero project impact). Phase 2 = all projects + file-intersection duplicate detection.
```

- [ ] **Step 2: Lint**

Run: `ruff check workflow_dashboard/`
Expected: `All checks passed!` (fix any reported issues, then re-run)

- [ ] **Step 3: Full test suite**

Run: `pytest tests/test_workflow_*.py`
Expected: all passed

- [ ] **Step 4: Confirm output is gitignored**

Run: `git status --porcelain workflow_dashboard/output`
Expected: empty output (folder ignored)

- [ ] **Step 5: Commit**

```bash
git add workflow_dashboard/README.md
git commit -m "docs(dashboard): add usage README (POS-92)"
```

---

## Self-Review

**Spec coverage:**
- Read-only aggregation of slot/jsonl/git → Tasks 2,3,4,6 ✅
- gstack timeline → confirmed absent at expected path; treated as optional/fail-safe (resolve returns none → skipped). Acceptable for MVP; can add as a source module in Phase 2.
- model.json + static HTML, zero deps/server → Tasks 6,7,8 ✅ (HTML self-contained, model embedded)
- 5 tangle rules → Task 5 ✅ (re-mapped to detectable signals; documented)
- 8-risk safety (read-only, idempotent, state-separated output, fail-safe) → enforced across parsers + Task 0 gitignore ✅
- 3-step rollback → README ✅
- Tests: aggregator unit tests + conflict-scenario tests → every task is TDD ✅
- Single-project MVP, on-demand, lives in dev-rules-starter-kit → ✅ (D1/D2/D3)

**Departures from the design's illustrative model (documented, intentional):**
1. Slots and sessions are **separate panels** (no slot↔sessionId key exists).
2. `duplicate_work` uses "≥2 in-progress slots" instead of file-set intersection (`files_touched` deferred to Phase 2).
3. Model embedded in HTML (not `fetch`ed) so it opens via `file://` with no server.

**Placeholder scan:** none — every code step is complete, runnable code.

**Type consistency:** dataclass field names are reused verbatim across tasks: `Slot(slot,topic,status,last_updated,note)`, `Session(id_short,title,branch,last_activity,live,pr)`, `GitInfo(branch,uncommitted,unpushed,commits_24h,worktrees)`, `Conflict(rule,severity,detail)`. `build_model`/`collect_git_info` share the `runner(args, cwd)->str` signature. `resolve_jsonl_dir` is defined in `model.py` and patched by the model test.
