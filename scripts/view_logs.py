#!/usr/bin/env python3
"""
Unified Log Viewer for Dev Rules Starter Kit

Purpose:
- View logs from all agents in one place
- Simplify debugging by aggregating scattered logs
- Support date-based filtering

Constitutional Compliance:
- [P6] Observability
- [P10] Windows UTF-8 (ASCII-only output)

Usage:
    python scripts/view_logs.py                    # Today's logs
    python scripts/view_logs.py 20251024           # Specific date
    python scripts/view_logs.py --agent devassist  # Specific agent
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json
import argparse


class LogViewer:
    """Unified log viewer for all agent logs"""

    def __init__(self, runs_dir: Path = Path("RUNS")):
        self.runs_dir = runs_dir

    def view_dev_assistant_logs(self, date: str) -> Optional[str]:
        """View DevAssistant logs"""
        log_path = self.runs_dir / f"dev-assistant-{date}" / "verification.log"

        if not log_path.exists():
            return None

        return log_path.read_text(encoding="utf-8")

    def view_evidence_logs(self, task_id: str) -> Optional[List[dict]]:
        """View evidence logs for a task"""
        evidence_dir = self.runs_dir / task_id / "evidence"

        if not evidence_dir.exists():
            return None

        evidence_files = sorted(evidence_dir.glob("*.json"))
        evidence_data = []

        for evidence_file in evidence_files:
            try:
                data = json.loads(evidence_file.read_text(encoding="utf-8"))
                evidence_data.append(
                    {
                        "file": evidence_file.name,
                        "data": data,
                    }
                )
            except Exception:
                continue

        return evidence_data if evidence_data else None

    def view_compression_reports(self) -> List[dict]:
        """View all compression reports"""
        report_files = sorted(self.runs_dir.glob("*/compression_report.json"))

        reports = []
        for report_file in report_files:
            try:
                data = json.loads(report_file.read_text(encoding="utf-8"))
                reports.append(
                    {
                        "task_id": data.get("task_id", "unknown"),
                        "summary": data.get("summary", {}),
                    }
                )
            except Exception:
                continue

        return reports

    def view_task_states(self) -> List[dict]:
        """View all task execution states"""
        state_files = sorted(self.runs_dir.glob("*/.state.json"))

        states = []
        for state_file in state_files:
            try:
                data = json.loads(state_file.read_text(encoding="utf-8"))
                task_id = state_file.parent.name
                states.append(
                    {
                        "task_id": task_id,
                        "status": data.get("status", "unknown"),
                        "evidence_count": data.get("evidence_count", 0),
                    }
                )
            except Exception:
                continue

        return states

    def view_stats(self) -> Optional[str]:
        """View team statistics dashboard"""
        stats_path = self.runs_dir / "stats" / "team_dashboard.md"

        if not stats_path.exists():
            return None

        return stats_path.read_text(encoding="utf-8")


def format_dev_assistant_logs(logs: str) -> str:
    """Format DevAssistant logs for display"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("[DEV ASSISTANT LOGS]")
    lines.append("=" * 80)
    lines.append(logs)
    return "\n".join(lines)


def format_evidence_logs(evidence: List[dict]) -> str:
    """Format evidence logs for display"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("[EVIDENCE LOGS]")
    lines.append("=" * 80)

    for item in evidence:
        lines.append(f"\n[FILE] {item['file']}")
        lines.append(json.dumps(item["data"], indent=2, ensure_ascii=False))

    return "\n".join(lines)


def format_compression_reports(reports: List[dict]) -> str:
    """Format compression reports for display"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("[COMPRESSION REPORTS]")
    lines.append("=" * 80)

    for report in reports:
        task_id = report["task_id"]
        summary = report["summary"]

        lines.append(f"\n[TASK] {task_id}")
        lines.append(f"  Prompts compressed: {summary.get('prompts_compressed', 0)}")
        lines.append(f"  Original tokens: {summary.get('total_original_tokens', 0)}")
        lines.append(f"  Compressed tokens: {summary.get('total_compressed_tokens', 0)}")
        lines.append(f"  Savings: {summary.get('average_savings_pct', 0):.1f}%")

    return "\n".join(lines)


def format_task_states(states: List[dict]) -> str:
    """Format task states for display"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("[TASK EXECUTION STATES]")
    lines.append("=" * 80)

    for state in states:
        status_icon = "[OK]" if state["status"] == "success" else "[FAIL]"
        lines.append(f"  {status_icon} {state['task_id']} ({state['evidence_count']} evidence files)")

    return "\n".join(lines)


def format_stats(stats: str) -> str:
    """Format team statistics for display"""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("[TEAM STATISTICS]")
    lines.append("=" * 80)
    lines.append(stats)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Unified log viewer for all agents")
    parser.add_argument("date", nargs="?", help="Date in YYYYMMDD format (default: today)")
    parser.add_argument(
        "--agent", choices=["devassist", "evidence", "compression", "tasks", "stats"], help="View specific agent logs only"
    )
    parser.add_argument("--task-id", help="Task ID for evidence logs")

    args = parser.parse_args()

    # Default to today
    date = args.date if args.date else datetime.now().strftime("%Y%m%d")

    viewer = LogViewer()

    # View specific agent or all
    if args.agent == "devassist":
        logs = viewer.view_dev_assistant_logs(date)
        if logs:
            print(format_dev_assistant_logs(logs))
        else:
            print(f"[WARN] No DevAssistant logs found for date: {date}")

    elif args.agent == "evidence":
        if not args.task_id:
            print("[ERROR] --task-id required for evidence logs")
            sys.exit(1)

        evidence = viewer.view_evidence_logs(args.task_id)
        if evidence:
            print(format_evidence_logs(evidence))
        else:
            print(f"[WARN] No evidence logs found for task: {args.task_id}")

    elif args.agent == "compression":
        reports = viewer.view_compression_reports()
        if reports:
            print(format_compression_reports(reports))
        else:
            print("[WARN] No compression reports found")

    elif args.agent == "tasks":
        states = viewer.view_task_states()
        if states:
            print(format_task_states(states))
        else:
            print("[WARN] No task states found")

    elif args.agent == "stats":
        stats = viewer.view_stats()
        if stats:
            print(format_stats(stats))
        else:
            print("[WARN] No team statistics found")

    else:
        # View all logs
        print("\n[UNIFIED LOG VIEWER]")
        print(f"Date: {date}")

        # DevAssistant
        dev_logs = viewer.view_dev_assistant_logs(date)
        if dev_logs:
            print(format_dev_assistant_logs(dev_logs))

        # Compression reports
        compression = viewer.view_compression_reports()
        if compression:
            print(format_compression_reports(compression))

        # Task states
        task_states = viewer.view_task_states()
        if task_states:
            print(format_task_states(task_states))

        # Team stats
        stats = viewer.view_stats()
        if stats:
            print(format_stats(stats))


if __name__ == "__main__":
    main()
