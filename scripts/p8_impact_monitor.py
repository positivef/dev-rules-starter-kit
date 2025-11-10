# -*- coding: utf-8 -*-
"""
P8 Impact Monitor - Track 80% coverage standard effectiveness

Monitors:
1. Test writing time (vs historical baseline)
2. Test coverage percentage
3. Quality metrics (bug escape rate)
4. ROI analysis (time saved vs quality maintained)

Usage:
    python scripts/p8_impact_monitor.py --record    # Record current metrics
    python scripts/p8_impact_monitor.py --report    # Generate weekly report
    python scripts/p8_impact_monitor.py --compare   # Compare with 90% baseline
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class P8ImpactMonitor:
    """Monitor P8 80% coverage standard impact"""

    def __init__(self, data_dir: str = "RUNS/p8_monitoring"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "metrics.jsonl"
        self.baseline_file = self.data_dir / "baseline_90percent.json"

    def record_metrics(
        self,
        test_writing_time: float,
        coverage_percent: float,
        tests_written: int,
        bugs_found_in_testing: int = 0,
        bugs_escaped_to_prod: int = 0,
        notes: str = "",
    ) -> None:
        """Record current session metrics"""

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "test_writing_time_minutes": test_writing_time,
            "coverage_percent": coverage_percent,
            "tests_written": tests_written,
            "bugs_found_in_testing": bugs_found_in_testing,
            "bugs_escaped_to_prod": bugs_escaped_to_prod,
            "notes": notes,
            "time_per_test": (
                test_writing_time / tests_written if tests_written > 0 else 0
            ),
        }

        # Append to JSONL
        with open(self.metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics) + "\n")

        print(f"[RECORDED] Metrics saved: {metrics['timestamp']}")
        print(f"  Coverage: {coverage_percent}%")
        print(f"  Time per test: {metrics['time_per_test']:.1f} min")

    def load_metrics(self, days: int = 7) -> List[Dict]:
        """Load metrics from last N days"""

        if not self.metrics_file.exists():
            return []

        cutoff = datetime.now() - timedelta(days=days)
        metrics = []

        with open(self.metrics_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line.strip())
                timestamp = datetime.fromisoformat(data["timestamp"])
                if timestamp >= cutoff:
                    metrics.append(data)

        return metrics

    def calculate_weekly_stats(self) -> Dict:
        """Calculate weekly statistics"""

        metrics = self.load_metrics(days=7)

        if not metrics:
            return {
                "error": "No data collected in the last 7 days",
                "recommendation": "Run with --record to start collecting data",
            }

        total_time = sum(m["test_writing_time_minutes"] for m in metrics)
        total_tests = sum(m["tests_written"] for m in metrics)
        avg_coverage = (
            sum(m["coverage_percent"] for m in metrics) / len(metrics)
            if metrics
            else 0
        )
        total_bugs_testing = sum(m["bugs_found_in_testing"] for m in metrics)
        total_bugs_prod = sum(m["bugs_escaped_to_prod"] for m in metrics)

        stats = {
            "period": "Last 7 days",
            "data_points": len(metrics),
            "total_time_minutes": total_time,
            "total_tests_written": total_tests,
            "avg_time_per_test": total_time / total_tests if total_tests > 0 else 0,
            "avg_coverage_percent": avg_coverage,
            "bugs_found_in_testing": total_bugs_testing,
            "bugs_escaped_to_prod": total_bugs_prod,
            "bug_escape_rate": (
                (total_bugs_prod / (total_bugs_testing + total_bugs_prod) * 100)
                if (total_bugs_testing + total_bugs_prod) > 0
                else 0
            ),
        }

        return stats

    def save_baseline(
        self,
        avg_time_per_test: float,
        avg_coverage: float,
        bug_escape_rate: float,
    ) -> None:
        """Save 90% baseline for comparison"""

        baseline = {
            "standard": "90% coverage (pre-2025-11-08)",
            "created": datetime.now().isoformat(),
            "avg_time_per_test_minutes": avg_time_per_test,
            "avg_coverage_percent": avg_coverage,
            "bug_escape_rate_percent": bug_escape_rate,
        }

        with open(self.baseline_file, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)

        print(f"[BASELINE] Saved 90% baseline to {self.baseline_file}")

    def compare_with_baseline(self) -> Dict:
        """Compare current 80% performance with 90% baseline"""

        if not self.baseline_file.exists():
            return {
                "error": "No baseline found",
                "recommendation": "Run with --baseline to set 90% baseline first",
            }

        with open(self.baseline_file, "r", encoding="utf-8") as f:
            baseline = json.load(f)

        current = self.calculate_weekly_stats()

        if "error" in current:
            return current

        comparison = {
            "baseline_90_percent": baseline,
            "current_80_percent": current,
            "improvements": {},
            "regressions": {},
            "verdict": "",
        }

        # Time per test comparison
        time_diff = baseline["avg_time_per_test_minutes"] - current["avg_time_per_test"]
        time_improvement_pct = (
            (time_diff / baseline["avg_time_per_test_minutes"] * 100)
            if baseline["avg_time_per_test_minutes"] > 0
            else 0
        )

        if time_diff > 0:
            comparison["improvements"]["time_per_test"] = {
                "saved_minutes": time_diff,
                "improvement_percent": time_improvement_pct,
                "message": f"FASTER by {time_diff:.1f} min/test ({time_improvement_pct:.1f}%)",
            }
        else:
            comparison["regressions"]["time_per_test"] = {
                "slower_minutes": abs(time_diff),
                "regression_percent": abs(time_improvement_pct),
                "message": f"SLOWER by {abs(time_diff):.1f} min/test ({abs(time_improvement_pct):.1f}%)",
            }

        # Coverage comparison
        coverage_diff = current["avg_coverage_percent"] - baseline["avg_coverage_percent"]
        if coverage_diff >= -2:  # Allow 2% tolerance
            comparison["improvements"]["coverage"] = {
                "difference": coverage_diff,
                "message": f"Coverage maintained ({coverage_diff:+.1f}%)",
            }
        else:
            comparison["regressions"]["coverage"] = {
                "difference": coverage_diff,
                "message": f"Coverage dropped ({coverage_diff:+.1f}%)",
            }

        # Bug escape rate comparison
        bug_diff = current["bug_escape_rate"] - baseline["bug_escape_rate_percent"]
        if bug_diff <= 2:  # Allow 2% tolerance
            comparison["improvements"]["quality"] = {
                "difference": bug_diff,
                "message": f"Quality maintained ({bug_diff:+.1f}% escape rate)",
            }
        else:
            comparison["regressions"]["quality"] = {
                "difference": bug_diff,
                "message": f"Quality degraded ({bug_diff:+.1f}% escape rate)",
            }

        # Verdict
        if not comparison["regressions"]:
            comparison["verdict"] = "SUCCESS: 80% standard is working well"
        elif len(comparison["regressions"]) == 1 and "time_per_test" in comparison["regressions"]:
            comparison["verdict"] = "ACCEPTABLE: Minor time regression only"
        else:
            comparison["verdict"] = "REVIEW NEEDED: Quality or coverage issues detected"

        return comparison

    def generate_report(self) -> str:
        """Generate weekly monitoring report"""

        stats = self.calculate_weekly_stats()
        comparison = self.compare_with_baseline()

        report = []
        report.append("=" * 60)
        report.append("P8 Impact Monitor - Weekly Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 60)
        report.append("")

        if "error" in stats:
            report.append(f"[ERROR] {stats['error']}")
            report.append(f"Recommendation: {stats['recommendation']}")
            return "\n".join(report)

        # Current stats
        report.append("CURRENT PERFORMANCE (80% Standard)")
        report.append("-" * 60)
        report.append(f"  Period: {stats['period']}")
        report.append(f"  Data points: {stats['data_points']}")
        report.append(f"  Avg coverage: {stats['avg_coverage_percent']:.1f}%")
        report.append(f"  Avg time/test: {stats['avg_time_per_test']:.1f} min")
        report.append(f"  Bug escape rate: {stats['bug_escape_rate']:.1f}%")
        report.append("")

        # Comparison with baseline
        if "error" not in comparison:
            report.append("COMPARISON WITH 90% BASELINE")
            report.append("-" * 60)

            if comparison["improvements"]:
                report.append("IMPROVEMENTS:")
                for key, data in comparison["improvements"].items():
                    report.append(f"  [SUCCESS] {data['message']}")
                report.append("")

            if comparison["regressions"]:
                report.append("REGRESSIONS:")
                for key, data in comparison["regressions"].items():
                    report.append(f"  [WARN] {data['message']}")
                report.append("")

            report.append(f"VERDICT: {comparison['verdict']}")
            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 60)

        if stats["avg_coverage_percent"] < 75:
            report.append("  [ACTION] Coverage below 75% - investigate why")
        elif stats["avg_coverage_percent"] < 80:
            report.append("  [WARN] Coverage below 80% - monitor closely")
        else:
            report.append("  [SUCCESS] Coverage meets 80% standard")

        if stats["bug_escape_rate"] > 10:
            report.append("  [ACTION] Bug escape rate >10% - review test quality")
        else:
            report.append("  [SUCCESS] Bug escape rate acceptable")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="P8 Impact Monitor")
    parser.add_argument("--record", action="store_true", help="Record current metrics")
    parser.add_argument("--report", action="store_true", help="Generate weekly report")
    parser.add_argument("--compare", action="store_true", help="Compare with baseline")
    parser.add_argument("--baseline", action="store_true", help="Set 90% baseline")

    # Recording parameters
    parser.add_argument("--time", type=float, help="Test writing time (minutes)")
    parser.add_argument("--coverage", type=float, help="Coverage percentage")
    parser.add_argument("--tests", type=int, help="Number of tests written")
    parser.add_argument("--bugs-testing", type=int, default=0, help="Bugs found in testing")
    parser.add_argument("--bugs-prod", type=int, default=0, help="Bugs escaped to production")
    parser.add_argument("--notes", type=str, default="", help="Session notes")

    # Baseline parameters
    parser.add_argument("--baseline-time", type=float, help="Baseline time per test")
    parser.add_argument("--baseline-coverage", type=float, help="Baseline coverage")
    parser.add_argument("--baseline-escape", type=float, help="Baseline bug escape rate")

    args = parser.parse_args()

    monitor = P8ImpactMonitor()

    if args.record:
        if not all([args.time, args.coverage, args.tests]):
            print("[ERROR] --record requires --time, --coverage, and --tests")
            return

        monitor.record_metrics(
            test_writing_time=args.time,
            coverage_percent=args.coverage,
            tests_written=args.tests,
            bugs_found_in_testing=args.bugs_testing,
            bugs_escaped_to_prod=args.bugs_prod,
            notes=args.notes,
        )

    elif args.baseline:
        if not all([args.baseline_time, args.baseline_coverage, args.baseline_escape]):
            print("[ERROR] --baseline requires --baseline-time, --baseline-coverage, --baseline-escape")
            return

        monitor.save_baseline(
            avg_time_per_test=args.baseline_time,
            avg_coverage=args.baseline_coverage,
            bug_escape_rate=args.baseline_escape,
        )

    elif args.report:
        report = monitor.generate_report()
        print(report)

        # Save report to file
        report_file = monitor.data_dir / f"report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n[SAVED] Report saved to {report_file}")

    elif args.compare:
        comparison = monitor.compare_with_baseline()
        print(json.dumps(comparison, indent=2))

    else:
        print("Use --record, --report, --compare, or --baseline")
        print("Run with --help for usage details")


if __name__ == "__main__":
    main()
