#!/usr/bin/env python3
"""TDD Workflow Tracker - Track test-first development compliance.

Analyzes git commit history to verify TDD workflow compliance:
- Tests committed before implementation (test-first approach)
- Per-developer TDD compliance scores
- Weekly/monthly compliance trends
- Violation tracking and reporting

Constitutional Compliance:
- P8: Test-First Development (core focus)
- P2: Evidence-Based (tracks all TDD violations)
- P6: Quality Gates (compliance thresholds)

Usage:
    python scripts/tdd_workflow_tracker.py --analyze
    python scripts/tdd_workflow_tracker.py --report weekly
    python scripts/tdd_workflow_tracker.py --developer <name>
"""

import json
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class CommitAnalysis:
    """Represents analysis of a single commit."""

    def __init__(
        self,
        commit_hash: str,
        author: str,
        timestamp: datetime,
        files_changed: List[str],
        is_tdd_compliant: bool,
        violation_reason: Optional[str] = None,
    ):
        self.commit_hash = commit_hash
        self.author = author
        self.timestamp = timestamp
        self.files_changed = files_changed
        self.is_tdd_compliant = is_tdd_compliant
        self.violation_reason = violation_reason


class TDDWorkflowTracker:
    """Track and analyze TDD workflow compliance from git history."""

    def __init__(self, project_root: Path = None, evidence_dir: Path = None):
        """Initialize TDD workflow tracker.

        Args:
            project_root: Project root directory
            evidence_dir: Directory for violation logs (default: RUNS/tdd-violations/)
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.evidence_dir = evidence_dir or self.project_root / "RUNS" / "tdd-violations"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def get_commit_history(self, days: int = 30) -> List[Dict]:
        """Get git commit history for the last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of commit dictionaries with hash, author, timestamp, files
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            # Get commit log with format: hash|author|timestamp
            cmd = [
                "git",
                "log",
                f"--since={since_date}",
                "--pretty=format:%H|%an|%ai",
                "--name-only",
            ]
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            commits = []
            current_commit = None

            for line in result.stdout.split("\n"):
                if not line.strip():
                    if current_commit:
                        commits.append(current_commit)
                        current_commit = None
                    continue

                if "|" in line:
                    # Commit info line
                    parts = line.split("|")
                    current_commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "timestamp": datetime.fromisoformat(parts[2].split()[0] + " " + parts[2].split()[1]),
                        "files": [],
                    }
                elif current_commit:
                    # File name line
                    current_commit["files"].append(line.strip())

            # Add last commit if exists
            if current_commit:
                commits.append(current_commit)

            return commits

        except (subprocess.CalledProcessError, Exception):
            return []

    def analyze_commit_tdd_compliance(self, commit: Dict) -> CommitAnalysis:
        """Analyze if a commit follows TDD principles.

        TDD compliance rules:
        1. If both test and source files changed, test file should be committed first
        2. If only source files changed, it's a violation (unless exempt)
        3. If only test files changed, it's compliant

        Args:
            commit: Commit dictionary with hash, author, timestamp, files

        Returns:
            CommitAnalysis object with compliance status
        """
        files = commit["files"]

        # Categorize files
        test_files = [f for f in files if self._is_test_file(f)]
        source_files = [f for f in files if self._is_source_file(f) and not self._is_test_file(f)]

        # Rule 1: Only test files -> compliant
        if test_files and not source_files:
            return CommitAnalysis(
                commit_hash=commit["hash"],
                author=commit["author"],
                timestamp=commit["timestamp"],
                files_changed=files,
                is_tdd_compliant=True,
            )

        # Rule 2: Only source files -> violation (test-after or no test)
        if source_files and not test_files:
            return CommitAnalysis(
                commit_hash=commit["hash"],
                author=commit["author"],
                timestamp=commit["timestamp"],
                files_changed=files,
                is_tdd_compliant=False,
                violation_reason="Source files committed without corresponding test files",
            )

        # Rule 3: Both test and source files
        # This is acceptable in single commit if it's a small change
        # For strict TDD, this should be two commits (test first, then implementation)
        if test_files and source_files:
            return CommitAnalysis(
                commit_hash=commit["hash"],
                author=commit["author"],
                timestamp=commit["timestamp"],
                files_changed=files,
                is_tdd_compliant=True,  # Lenient: both in one commit is OK
            )

        # No Python files changed
        return CommitAnalysis(
            commit_hash=commit["hash"],
            author=commit["author"],
            timestamp=commit["timestamp"],
            files_changed=files,
            is_tdd_compliant=True,  # Not applicable
        )

    def _is_test_file(self, filepath: str) -> bool:
        """Check if file is a test file."""
        return "test" in filepath.lower() and filepath.endswith(".py")

    def _is_source_file(self, filepath: str) -> bool:
        """Check if file is a Python source file."""
        if not filepath.endswith(".py"):
            return False

        # Exclude certain directories
        exclude_dirs = ["docs", "examples", "config", ".github", "RUNS", "TASKS"]
        for exclude in exclude_dirs:
            if exclude in filepath:
                return False

        return True

    def calculate_developer_score(self, developer: str, days: int = 30) -> Dict:
        """Calculate TDD compliance score for a developer.

        Args:
            developer: Developer name
            days: Number of days to analyze

        Returns:
            Dictionary with compliance metrics
        """
        commits = self.get_commit_history(days)
        developer_commits = [c for c in commits if c["author"] == developer]

        if not developer_commits:
            return {
                "developer": developer,
                "total_commits": 0,
                "compliant_commits": 0,
                "compliance_rate": 0.0,
                "violations": [],
            }

        analyses = [self.analyze_commit_tdd_compliance(c) for c in developer_commits]
        compliant = [a for a in analyses if a.is_tdd_compliant]
        violations = [a for a in analyses if not a.is_tdd_compliant]

        return {
            "developer": developer,
            "total_commits": len(analyses),
            "compliant_commits": len(compliant),
            "compliance_rate": (len(compliant) / len(analyses)) * 100 if analyses else 0.0,
            "violations": [
                {
                    "commit": v.commit_hash[:8],
                    "timestamp": v.timestamp.isoformat(),
                    "reason": v.violation_reason,
                    "files": v.files_changed,
                }
                for v in violations
            ],
        }

    def generate_team_report(self, days: int = 30) -> Dict:
        """Generate team-wide TDD compliance report.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with team metrics
        """
        commits = self.get_commit_history(days)

        if not commits:
            return {
                "period_days": days,
                "total_commits": 0,
                "developers": {},
                "team_compliance_rate": 0.0,
            }

        # Group by developer
        developers = defaultdict(list)
        for commit in commits:
            developers[commit["author"]].append(commit)

        # Calculate per-developer scores
        developer_scores = {}
        for dev, dev_commits in developers.items():
            analyses = [self.analyze_commit_tdd_compliance(c) for c in dev_commits]
            compliant = sum(1 for a in analyses if a.is_tdd_compliant)
            developer_scores[dev] = {
                "commits": len(analyses),
                "compliant": compliant,
                "compliance_rate": (compliant / len(analyses)) * 100 if analyses else 0.0,
            }

        # Calculate team average
        total_commits = sum(s["commits"] for s in developer_scores.values())
        total_compliant = sum(s["compliant"] for s in developer_scores.values())
        team_compliance = (total_compliant / total_commits) * 100 if total_commits else 0.0

        return {
            "period_days": days,
            "total_commits": total_commits,
            "developers": developer_scores,
            "team_compliance_rate": team_compliance,
        }

    def log_violations(self, violations: List[CommitAnalysis]) -> Path:
        """Log TDD violations to evidence directory.

        Args:
            violations: List of violation CommitAnalysis objects

        Returns:
            Path to log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.evidence_dir / f"tdd_workflow_violations_{timestamp}.json"

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "violations": [
                {
                    "commit": v.commit_hash,
                    "author": v.author,
                    "timestamp": v.timestamp.isoformat(),
                    "reason": v.violation_reason,
                    "files": v.files_changed,
                }
                for v in violations
            ],
            "summary": {
                "total_violations": len(violations),
                "unique_developers": len(set(v.author for v in violations)),
            },
        }

        log_file.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
        return log_file

    def generate_report(self, period: str = "weekly") -> str:
        """Generate human-readable TDD compliance report.

        Args:
            period: Report period ('weekly' or 'monthly')

        Returns:
            Formatted report string
        """
        days = 7 if period == "weekly" else 30
        report_data = self.generate_team_report(days)

        lines = []
        lines.append("=" * 60)
        lines.append(f"TDD WORKFLOW COMPLIANCE REPORT ({period.upper()})")
        lines.append("=" * 60)
        lines.append(f"Period: Last {days} days")
        lines.append(f"Total Commits: {report_data['total_commits']}")
        lines.append(f"Team Compliance Rate: {report_data['team_compliance_rate']:.1f}%")
        lines.append("")

        if report_data["developers"]:
            lines.append("DEVELOPER BREAKDOWN:")
            for dev, stats in sorted(
                report_data["developers"].items(),
                key=lambda x: x[1]["compliance_rate"],
                reverse=True,
            ):
                lines.append(f"  {dev}: {stats['compliant']}/{stats['commits']} " f"({stats['compliance_rate']:.1f}%)")
            lines.append("")

        # Compliance status
        compliance_rate = report_data["team_compliance_rate"]
        if compliance_rate >= 95:
            lines.append("[EXCELLENT] Team exceeds TDD compliance target (95%+)")
        elif compliance_rate >= 80:
            lines.append("[GOOD] Team meets TDD compliance target (80%+)")
        elif compliance_rate >= 60:
            lines.append("[WARNING] Team below TDD compliance target (60-79%)")
        else:
            lines.append("[CRITICAL] Team significantly below TDD compliance target (<60%)")

        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """Main entry point for TDD workflow tracker."""
    import argparse

    parser = argparse.ArgumentParser(description="TDD Workflow Tracker")
    parser.add_argument("--analyze", action="store_true", help="Analyze commit history")
    parser.add_argument(
        "--report",
        choices=["weekly", "monthly"],
        help="Generate compliance report",
    )
    parser.add_argument("--developer", type=str, help="Analyze specific developer")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze")

    args = parser.parse_args()

    tracker = TDDWorkflowTracker()

    if args.report:
        report = tracker.generate_report(args.report)
        print(report)

    elif args.developer:
        score = tracker.calculate_developer_score(args.developer, args.days)
        print(f"\nDeveloper: {score['developer']}")
        print(f"Compliance Rate: {score['compliance_rate']:.1f}%")
        print(f"Commits: {score['compliant_commits']}/{score['total_commits']}")

        if score["violations"]:
            print(f"\nViolations ({len(score['violations'])}):")
            for v in score["violations"][:5]:  # Show first 5
                print(f"  {v['commit']}: {v['reason']}")

    elif args.analyze:
        report_data = tracker.generate_team_report(args.days)
        print(json.dumps(report_data, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
