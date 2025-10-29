#!/usr/bin/env python3
"""Preflight checks for collaboration-critical components."""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Iterable, List, Tuple

TESTS: List[Tuple[str, List[str]]] = [
    ("enhanced-executor", [sys.executable, "-m", "pytest", "-q", "tests/test_enhanced_task_executor_v2.py"]),
    ("handoff-protocol", [sys.executable, "-m", "pytest", "-q", "tests/test_handoff_protocol.py"]),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run collaboration preflight checks")
    parser.add_argument("--quick", action="store_true", help="Run only essential tests (skip handoff protocol)")
    parser.add_argument("--skip-handoff", action="store_true", help="Skip handoff protocol test")
    parser.add_argument("--only-handoff", action="store_true", help="Run only the handoff protocol test")
    parser.add_argument("--list", action="store_true", help="List configured checks without executing")
    return parser


def select_checks(args: argparse.Namespace) -> List[Tuple[str, List[str]]]:
    if args.only_handoff:
        return [item for item in TESTS if item[0] == "handoff-protocol"]

    selected: List[Tuple[str, List[str]]] = []
    for name, cmd in TESTS:
        if args.quick and name != "enhanced-executor":
            continue
        if args.skip_handoff and name == "handoff-protocol":
            continue
        selected.append((name, cmd))
    return selected


def run_checks(checks: Iterable[Tuple[str, List[str]]]) -> int:
    for name, cmd in checks:
        print(f"[CHECK:{name}] {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"[FAIL:{name}] {' '.join(cmd)}")
            return result.returncode
        print(f"[OK:{name}]")
    print("[DONE] All preflight checks passed")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    checks = select_checks(args)

    if args.list:
        for name, cmd in checks:
            print(f"{name}: {' '.join(cmd)}")
        return 0

    if not checks:
        print("[WARN] No checks selected. Use --list to see available options.")
        return 0

    return run_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())
