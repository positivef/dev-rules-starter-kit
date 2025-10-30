#!/usr/bin/env python3
"""Render current lock/conflict status as an ASCII dashboard."""

from __future__ import annotations

from typing import Iterable, List

from agent_sync import get_active_locks, detect_conflicts


def summarize_locks() -> List[str]:
    locks = get_active_locks()
    if not locks:
        return ["No active locks."]
    lines: List[str] = ["Active Locks:"]
    by_agent: dict[str, List[dict]] = {}
    for lock in locks:
        by_agent.setdefault(lock.get("agent_id", "<unknown>"), []).append(lock)
    for agent, items in sorted(by_agent.items()):
        lines.append(f"- {agent} ({len(items)} file(s))")
        for lock in items:
            file_path = lock.get("file", "<unknown>")
            task = lock.get("task_id", "<unknown>")
            lines.append(f"    • {file_path} (task={task})")
    return lines


def summarize_conflicts(agent_id: str, files: Iterable[str]) -> List[str]:
    conflicts = detect_conflicts(agent_id, "", files)
    if not conflicts:
        return ["No conflicts detected for planned files."]
    lines = ["Potential Conflicts:"]
    for conflict in conflicts:
        file_path = conflict.get("file", "<unknown>")
        owner = conflict.get("agent_id", "<unknown>")
        task = conflict.get("task_id", "<unknown>")
        lines.append(f"- {file_path} held by {owner} (task={task})")
    return lines


def render_dashboard(agent_id: str, files: Iterable[str]) -> str:
    sections = ["COLLAB LOCK DASHBOARD", "===================="]
    sections.extend(summarize_locks())
    sections.append("")
    sections.extend(summarize_conflicts(agent_id, files))
    return "\n".join(sections)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Print lock/conflict dashboard")
    parser.add_argument("--agent", required=True, help="Prospective agent id")
    parser.add_argument("--files", nargs="*", default=[], help="Planned files")
    args = parser.parse_args()

    print(render_dashboard(args.agent, args.files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
