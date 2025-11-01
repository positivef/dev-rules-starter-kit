#!/usr/bin/env python3
"""TDD Metrics Tracker - Monitor test coverage and TDD compliance over time

Tracks key TDD metrics:
- Coverage percentage trends
- Test/Code ratio
- Test count growth
- Coverage velocity

Usage:
    python scripts/tdd_metrics.py record    # Record current metrics
    python scripts/tdd_metrics.py report    # Show metrics report
    python scripts/tdd_metrics.py trend     # Show coverage trend
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess


class TDDMetrics:
    """Track and analyze TDD metrics over time"""

    def __init__(self, metrics_file: Path = None):
        self.project_root = Path(__file__).parent.parent
        self.metrics_file = metrics_file or (self.project_root / "RUNS" / "tdd_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def load_metrics(self) -> Dict:
        """Load historical metrics"""
        if not self.metrics_file.exists():
            return {"history": [], "latest": None}

        with open(self.metrics_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_metrics(self, data: Dict) -> None:
        """Save metrics to file"""
        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_current_coverage(self) -> Optional[Dict]:
        """Get current coverage from coverage.json if available"""
        coverage_file = self.project_root / "coverage.json"

        if not coverage_file.exists():
            return None

        try:
            with open(coverage_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "percent_covered": data["totals"]["percent_covered"],
                "covered_lines": data["totals"]["covered_lines"],
                "num_statements": data["totals"]["num_statements"],
                "missing_lines": data["totals"]["missing_lines"],
            }
        except (KeyError, json.JSONDecodeError):
            return None

    def count_tests(self) -> Dict:
        """Count number of tests in the project"""
        test_dirs = [
            self.project_root / "tests",
            self.project_root / "tests" / "unit",
            self.project_root / "tests" / "integration",
        ]

        total_tests = 0
        unit_tests = 0
        integration_tests = 0

        for test_dir in test_dirs:
            if not test_dir.exists():
                continue

            for test_file in test_dir.rglob("test_*.py"):
                try:
                    content = test_file.read_text(encoding="utf-8")
                    # Count test functions (simple heuristic)
                    file_tests = content.count("def test_")
                    total_tests += file_tests

                    if "unit" in str(test_file):
                        unit_tests += file_tests
                    elif "integration" in str(test_file):
                        integration_tests += file_tests

                except Exception:
                    continue

        return {
            "total": total_tests,
            "unit": unit_tests,
            "integration": integration_tests,
        }

    def count_code_lines(self) -> int:
        """Count total lines of code in scripts/"""
        scripts_dir = self.project_root / "scripts"
        total_lines = 0

        if scripts_dir.exists():
            for py_file in scripts_dir.rglob("*.py"):
                try:
                    lines = py_file.read_text(encoding="utf-8").splitlines()
                    # Count non-empty, non-comment lines
                    code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                    total_lines += len(code_lines)
                except Exception:
                    continue

        return total_lines

    def get_git_commit_hash(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def record_metrics(self) -> Dict:
        """Record current TDD metrics"""
        coverage_data = self.get_current_coverage()
        test_counts = self.count_tests()
        code_lines = self.count_code_lines()

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "git_commit": self.get_git_commit_hash(),
            "coverage": coverage_data,
            "tests": test_counts,
            "code_lines": code_lines,
            "test_code_ratio": (test_counts["total"] / code_lines if code_lines > 0 else 0),
        }

        # Load and update historical data
        data = self.load_metrics()
        data["history"].append(metrics)
        data["latest"] = metrics

        # Keep last 100 records
        if len(data["history"]) > 100:
            data["history"] = data["history"][-100:]

        self.save_metrics(data)

        return metrics

    def calculate_trend(self, history: List[Dict], key_path: List[str]) -> Dict:
        """Calculate trend for a metric

        Args:
            history: List of historical metrics
            key_path: Path to metric (e.g., ["coverage", "percent_covered"])

        Returns:
            Dict with trend info (delta, velocity, direction)
        """
        if len(history) < 2:
            return {"delta": 0, "velocity": 0, "direction": "stable"}

        # Get values
        values = []
        for record in history:
            value = record
            for key in key_path:
                if value and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is not None:
                values.append(float(value))

        if len(values) < 2:
            return {"delta": 0, "velocity": 0, "direction": "stable"}

        # Calculate delta and velocity
        delta = values[-1] - values[-2]
        avg_change = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0

        direction = "up" if delta > 0 else ("down" if delta < 0 else "stable")

        return {
            "delta": round(delta, 2),
            "velocity": round(avg_change, 2),
            "direction": direction,
            "current": round(values[-1], 2),
            "previous": round(values[-2], 2) if len(values) > 1 else None,
        }

    def generate_report(self) -> str:
        """Generate TDD metrics report"""
        data = self.load_metrics()

        if not data.get("latest"):
            return "No metrics recorded yet. Run: python scripts/tdd_metrics.py record"

        latest = data["latest"]
        history = data["history"]

        # Calculate trends
        coverage_trend = self.calculate_trend(history, ["coverage", "percent_covered"])
        test_trend = self.calculate_trend(history, ["tests", "total"])

        # Build report
        lines = [
            "=" * 60,
            "TDD Metrics Report",
            "=" * 60,
            "",
            f"Timestamp: {latest['timestamp']}",
            f"Git Commit: {latest.get('git_commit', 'N/A')}",
            "",
            "Coverage:",
        ]

        if latest.get("coverage"):
            cov = latest["coverage"]
            lines.extend(
                [
                    f"  Current: {cov['percent_covered']:.2f}%",
                    f"  Lines: {cov['covered_lines']}/{cov['num_statements']}",
                    f"  Missing: {cov['missing_lines']}",
                ]
            )

            if coverage_trend["direction"] != "stable":
                symbol = "UP" if coverage_trend["direction"] == "up" else "DOWN"
                lines.append(
                    f"  Trend: [{symbol}] {coverage_trend['direction']} " f"({coverage_trend['delta']:+.2f}% from last)"
                )
        else:
            lines.append("  No coverage data available")
            lines.append("  Run: pytest tests/unit/ --cov=scripts --cov-report=json")

        lines.extend(
            [
                "",
                "Tests:",
                f"  Total: {latest['tests']['total']}",
                f"  Unit: {latest['tests']['unit']}",
                f"  Integration: {latest['tests']['integration']}",
            ]
        )

        if test_trend["direction"] != "stable":
            symbol = "UP" if test_trend["direction"] == "up" else "DOWN"
            lines.append(f"  Trend: [{symbol}] {test_trend['direction']} " f"({test_trend['delta']:+.0f} tests from last)")

        lines.extend(
            [
                "",
                "Code Metrics:",
                f"  Code Lines: {latest['code_lines']:,}",
                f"  Test/Code Ratio: {latest['test_code_ratio']:.3f}",
                f"  Tests per 100 LOC: {(latest['test_code_ratio'] * 100):.1f}",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    def show_trend(self, metric: str = "coverage") -> str:
        """Show trend visualization for a metric"""
        data = self.load_metrics()
        history = data.get("history", [])

        if len(history) < 2:
            return "Insufficient data for trend (need at least 2 records)"

        # Get coverage values
        values = []
        timestamps = []

        for record in history[-20:]:  # Last 20 records
            if metric == "coverage" and record.get("coverage"):
                values.append(record["coverage"]["percent_covered"])
                timestamps.append(record["timestamp"][:10])  # Date only
            elif metric == "tests":
                values.append(record["tests"]["total"])
                timestamps.append(record["timestamp"][:10])

        if not values:
            return f"No data for metric: {metric}"

        # Simple ASCII chart
        lines = [
            f"\n{metric.capitalize()} Trend (last {len(values)} records)",
            "=" * 60,
        ]

        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val if max_val != min_val else 1

        for i, (val, ts) in enumerate(zip(values, timestamps)):
            # Normalize to 0-40 range for bar
            bar_len = int(((val - min_val) / range_val) * 40)
            bar = "#" * bar_len
            lines.append(f"{ts}: {bar} {val:.2f}")

        lines.extend(
            [
                "=" * 60,
                f"Range: {min_val:.2f} - {max_val:.2f}",
                f"Latest: {values[-1]:.2f}",
                f"Change: {values[-1] - values[0]:+.2f}",
                "",
            ]
        )

        return "\n".join(lines)


def main():
    """Main CLI entry point"""
    metrics = TDDMetrics()

    command = sys.argv[1] if len(sys.argv) > 1 else "report"

    if command == "record":
        print("Recording TDD metrics...")
        result = metrics.record_metrics()
        print(f"[OK] Metrics recorded at {result['timestamp']}")
        if result.get("coverage"):
            print(f"  Coverage: {result['coverage']['percent_covered']:.2f}%")
        print(f"  Tests: {result['tests']['total']}")

    elif command == "report":
        print(metrics.generate_report())

    elif command == "trend":
        metric_type = sys.argv[2] if len(sys.argv) > 2 else "coverage"
        print(metrics.show_trend(metric_type))

    else:
        print("Usage:")
        print("  python scripts/tdd_metrics.py record    # Record current metrics")
        print("  python scripts/tdd_metrics.py report    # Show metrics report")
        print("  python scripts/tdd_metrics.py trend [coverage|tests]  # Show trend")
        sys.exit(1)


if __name__ == "__main__":
    main()
