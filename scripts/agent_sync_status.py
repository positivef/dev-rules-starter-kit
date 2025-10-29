#!/usr/bin/env python3
"""Display agent sync status and detect potential file-lock conflicts."""

from __future__ import annotations

import argparse
from typing import Iterable, List

from agent_sync import get_active_locks, detect_conflicts


def format_lock(lock: dict) -> str:
    file_path = lock.get("file", "<unknown>")
    agent = lock.get("agent_id", "<unknown>")
    task = lock.get("task_id", "<unknown>")
    locked_at = lock.get("locked_at", "<unknown>")
    return f"- {file_path} (agent={agent}, task={task}, locked_at={locked_at})"


def print_active_locks() -> None:
    locks = get_active_locks()
    if not locks:
        print("[INFO] No active locks recorded.")
        return

    print("[INFO] Active locks:")
    by_agent: dict[str, List[dict]] = {}
    for lock in locks:
        by_agent.setdefault(lock.get("agent_id", "<unknown>"), []).append(lock)

    for agent, entries in sorted(by_agent.items()):
        print(f"  Agent {agent} ({len(entries)} file(s)):")
        for entry in entries:
            print("    " + format_lock(entry))


def check_conflicts(agent_id: str, task_id: str, files: Iterable[str]) -> None:
    conflicts = detect_conflicts(agent_id, task_id, files)
    if not conflicts:
        print("[OK] No conflicts detected for requested files.")
        return

    print("[WARN] Conflicts detected:")
    for entry in conflicts:
        print("  " + format_lock(entry))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect agent sync locks and conflicts")
    parser.add_argument("--agent", help="Prospective agent id for conflict check")
    parser.add_argument("--task", help="Prospective task id for conflict check", default="")
    parser.add_argument("--files", nargs="*", help="Files to test for conflicts")
    parser.add_argument("--no-active", action="store_true", help="Skip printing active locks")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.no_active:
        print_active_locks()
        print()

    if args.files and args.agent:
        check_conflicts(args.agent, args.task or "", args.files)
    elif args.files and not args.agent:
        parser.error("--agent is required when --files are provided")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
