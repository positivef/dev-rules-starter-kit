"""Generate a compact observability summary for Dev Rules Starter Kit.

The script inspects key data sources (agent sync board, context comparison,
recent RUNS) and prints a human-readable digest. Optionally it can send the
summary to Slack if the environment provides a webhook URL.

Usage:
  python scripts/observability_report.py                # print summary
  python scripts/observability_report.py --slack        # print + send Slack
  python scripts/observability_report.py --limit 5      # include 5 recent runs
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Local imports
from context_compare import compare
from notification_utils import send_slack_notification

ROOT = Path(__file__).resolve().parent.parent
BOARD_PATH = ROOT / "dev-context" / "agent_sync_state.json"
RUNS_PATH = ROOT / "RUNS"


def load_agent_board() -> List[Dict[str, str]]:
    if not BOARD_PATH.exists():
        return []
    try:
        data = json.loads(BOARD_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    return []


def recent_runs(limit: int) -> List[str]:
    if not RUNS_PATH.exists():
        return []

    entries: List[tuple[float, Path]] = []
    for path in RUNS_PATH.iterdir():
        if not path.is_dir():
            continue
        state_file = path / ".state.json"
        if state_file.exists():
            entries.append((state_file.stat().st_mtime, path))
        else:
            entries.append((path.stat().st_mtime, path))

    entries.sort(reverse=True)
    summary = []
    for _, path in entries[:limit]:
        task_id = path.name
        state_file = path / ".state.json"
        status = "unknown"
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
                status = state.get("status", "unknown")
            except json.JSONDecodeError:
                pass
        ts = datetime.fromtimestamp(path.stat().st_mtime).isoformat(sep=" ", timespec="minutes")
        summary.append(f"{task_id}: {status} @ {ts}")
    return summary


def extract_lessons_summary(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "Unable to read lessons."

    summary: List[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## summary"):
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped:
            summary.append(stripped)

    if not summary:
        return "No summary yet."

    joined = " ".join(summary[:2])
    if "TODO" in joined.upper():
        return "Summary pending."
    return joined


def recent_lessons(limit: int) -> List[str]:
    entries: List[str] = []
    if not RUNS_PATH.exists():
        return entries

    sorted_tasks = sorted(
        [p for p in RUNS_PATH.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for task_dir in sorted_tasks:
        lessons_path = task_dir / "lessons.md"
        if lessons_path.exists():
            summary = extract_lessons_summary(lessons_path)
            entries.append(f"{task_dir.name}: {summary}")
        if len(entries) >= limit:
            break

    return entries


def recent_prompt_feedback(limit: int) -> List[str]:
    entries: List[str] = []
    if not RUNS_PATH.exists():
        return entries

    sorted_tasks = sorted(
        [p for p in RUNS_PATH.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for task_dir in sorted_tasks:
        feedback_path = task_dir / "prompt_feedback.json"
        if not feedback_path.exists():
            continue
        try:
            data = json.loads(feedback_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            entries.append(f"{task_dir.name}: unable to read prompt feedback")
            continue

        summary = data.get("summary") or {}
        avg = summary.get("average_savings_pct")
        total = summary.get("total_prompts")
        top = data.get("top_prompt", {})
        parts = []
        if total:
            parts.append(f"{total} prompts")
        if avg is not None:
            parts.append(f"avg savings {avg}%")
        top_cmd = top.get("command_id")
        if top_cmd:
            parts.append(f"top {top_cmd}: {top.get('savings_pct')}%")
        if not parts:
            parts.append("no successful compression data")
        if data.get("errors"):
            parts.append(f"errors: {len(data['errors'])}")

        entries.append(f"{task_dir.name}: {'; '.join(parts)}")

        if len(entries) >= limit:
            break

    return entries


def summarize_context() -> List[str]:
    lines: List[str] = []
    comparison = compare()
    legacy_env = comparison["legacy"].get("env", {})
    c7_env = comparison["c7"]["context"].get("env", {})

    if legacy_env != c7_env:
        lines.append("Context diff detected between legacy and C7 env values:")
        for key in sorted(set(legacy_env) | set(c7_env)):
            legacy_val = legacy_env.get(key)
            c7_val = c7_env.get(key)
            if legacy_val != c7_val:
                lines.append(f"  - {key}: legacy={legacy_val!r}, c7={c7_val!r}")
    else:
        lines.append("Context env values aligned (legacy vs C7)")

    validation_commands = (
        comparison["c7"]["context"]
        .get("master_config", {})
        .get("precision_system", {})
        .get("orchestration_policy", {})
        .get("auto_validation_commands", [])
    )
    if validation_commands:
        lines.append("Auto validation commands: " + ", ".join(validation_commands))
    return lines


def format_summary(limit: int) -> str:
    lines: List[str] = []

    lines.append(f"📊 Dev Rules Observability Report — {datetime.now().isoformat(timespec='minutes')}")
    lines.append("\nAgent Sync Board:")
    board = load_agent_board()
    if board:
        for status in board:
            agent = status.get("agent", "unknown")
            focus = status.get("focus", "-")
            ctx_hash = status.get("context_hash", "-")
            updated = status.get("updated_at", "-")
            lines.append(f"  - {agent}: {focus} (hash={ctx_hash}, updated={updated})")
    else:
        lines.append("  - No agent status recorded")

    lines.append("\nContext Synopsis:")
    lines.extend([f"  {line}" for line in summarize_context()])

    lines.append("\nRecent RUNS:")
    runs = recent_runs(limit)
    if runs:
        lines.extend([f"  - {entry}" for entry in runs])
    else:
        lines.append("  - No RUNS directories found")

    lines.append("\nLearning Highlights:")
    lessons = recent_lessons(limit)
    if lessons:
        lines.extend([f"  - {entry}" for entry in lessons])
    else:
        lines.append("  - No lessons recorded yet")

    lines.append("\nPrompt Feedback:")
    prompts = recent_prompt_feedback(limit)
    if prompts:
        lines.extend([f"  - {entry}" for entry in prompts])
    else:
        lines.append("  - No prompt feedback recorded yet")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate observability summary")
    parser.add_argument("--limit", type=int, default=3, help="Number of recent RUNS entries to include")
    parser.add_argument("--slack", action="store_true", help="Send the summary to Slack webhook if available")
    args = parser.parse_args()

    summary = format_summary(limit=max(1, args.limit))
    print(summary)

    if args.slack:
        sent = send_slack_notification(summary)
        if not sent:
            print("[WARN] Summary was not sent to Slack (webhook missing or request failed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
