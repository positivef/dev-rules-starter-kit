# -*- coding: utf-8 -*-
"""
Pattern 4 Impact Monitor - Track Design Review First effectiveness

Monitors:
1. Design review compliance rate
2. Risk detection rate
3. Post-implementation issue prevention
4. Time ROI (design time vs bug-fix time saved)

Usage:
    # Record design review
    python scripts/pattern4_impact_monitor.py --record-review \
        --feature "Auth middleware" --time 25 --risks 3 --mitigated 3

    # Record implementation
    python scripts/pattern4_impact_monitor.py --record-impl \
        --feature "Auth middleware" --bugs 0 --rollback false

    # Generate weekly report
    python scripts/pattern4_impact_monitor.py --report
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class Pattern4ImpactMonitor:
    """Monitor Pattern 4 Design Review First effectiveness"""

    def __init__(self, data_dir: str = "RUNS/pattern4_monitoring"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reviews_file = self.data_dir / "design_reviews.jsonl"
        self.impls_file = self.data_dir / "implementations.jsonl"
        self.baseline_file = self.data_dir / "baseline.json"

    def record_design_review(
        self,
        feature: str,
        review_time: float,
        risks_found: int,
        risks_mitigated: int,
        approved: bool = True,
        notes: str = "",
    ) -> None:
        """Record design review metrics"""

        review = {
            "timestamp": datetime.now().isoformat(),
            "feature": feature,
            "review_time_minutes": review_time,
            "risks_found": risks_found,
            "risks_mitigated": risks_mitigated,
            "approved": approved,
            "notes": notes,
            "mitigation_rate": ((risks_mitigated / risks_found * 100) if risks_found > 0 else 100),
        }

        # Append to JSONL
        with open(self.reviews_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(review) + "\n")

        print(f"[RECORDED] Design review saved: {feature}")
        print(f"  Review time: {review_time} min")
        print(f"  Risks found: {risks_found}")
        print(f"  Risks mitigated: {risks_mitigated} ({review['mitigation_rate']:.0f}%)")

    def record_implementation(
        self,
        feature: str,
        bugs_found: int,
        rollback_needed: bool,
        design_review_done: bool = True,
        notes: str = "",
    ) -> None:
        """Record implementation results"""

        impl = {
            "timestamp": datetime.now().isoformat(),
            "feature": feature,
            "design_review_done": design_review_done,
            "bugs_found": bugs_found,
            "rollback_needed": rollback_needed,
            "notes": notes,
        }

        # Append to JSONL
        with open(self.impls_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(impl) + "\n")

        print(f"[RECORDED] Implementation saved: {feature}")
        print(f"  Design review done: {design_review_done}")
        print(f"  Bugs found: {bugs_found}")
        print(f"  Rollback needed: {rollback_needed}")

    def load_reviews(self, days: int = 7) -> List[Dict]:
        """Load design reviews from last N days"""

        if not self.reviews_file.exists():
            return []

        cutoff = datetime.now() - timedelta(days=days)
        reviews = []

        with open(self.reviews_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line.strip())
                timestamp = datetime.fromisoformat(data["timestamp"])
                if timestamp >= cutoff:
                    reviews.append(data)

        return reviews

    def load_implementations(self, days: int = 7) -> List[Dict]:
        """Load implementations from last N days"""

        if not self.impls_file.exists():
            return []

        cutoff = datetime.now() - timedelta(days=days)
        impls = []

        with open(self.impls_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line.strip())
                timestamp = datetime.fromisoformat(data["timestamp"])
                if timestamp >= cutoff:
                    impls.append(data)

        return impls

    def calculate_weekly_stats(self) -> Dict:
        """Calculate weekly statistics"""

        reviews = self.load_reviews(days=7)
        impls = self.load_implementations(days=7)

        if not reviews and not impls:
            return {
                "error": "No data collected in the last 7 days",
                "recommendation": "Run with --record-review or --record-impl to start collecting data",
            }

        # Design review stats
        total_features = len(reviews)
        total_review_time = sum(r["review_time_minutes"] for r in reviews)
        total_risks_found = sum(r["risks_found"] for r in reviews)
        total_risks_mitigated = sum(r["risks_mitigated"] for r in reviews)

        # Implementation stats
        impl_with_review = [i for i in impls if i["design_review_done"]]
        impl_without_review = [i for i in impls if not i["design_review_done"]]

        bugs_with_review = sum(i["bugs_found"] for i in impl_with_review)
        bugs_without_review = sum(i["bugs_found"] for i in impl_without_review)

        rollbacks_with_review = sum(1 for i in impl_with_review if i["rollback_needed"])
        rollbacks_without_review = sum(1 for i in impl_without_review if i["rollback_needed"])

        stats = {
            "period": "Last 7 days",
            # Design review metrics
            "design_reviews": {
                "total": total_features,
                "total_time_minutes": total_review_time,
                "avg_time_per_review": (total_review_time / total_features if total_features > 0 else 0),
                "total_risks_found": total_risks_found,
                "total_risks_mitigated": total_risks_mitigated,
                "avg_risks_per_review": (total_risks_found / total_features if total_features > 0 else 0),
                "mitigation_rate": ((total_risks_mitigated / total_risks_found * 100) if total_risks_found > 0 else 100),
            },
            # Implementation metrics
            "implementations": {
                "total": len(impls),
                "with_review": len(impl_with_review),
                "without_review": len(impl_without_review),
                "compliance_rate": ((len(impl_with_review) / len(impls) * 100) if impls else 0),
            },
            # Quality metrics
            "quality": {
                "bugs_with_review": bugs_with_review,
                "bugs_without_review": bugs_without_review,
                "bug_rate_with_review": ((bugs_with_review / len(impl_with_review) * 100) if impl_with_review else 0),
                "bug_rate_without_review": (
                    (bugs_without_review / len(impl_without_review) * 100) if impl_without_review else 0
                ),
                "rollbacks_with_review": rollbacks_with_review,
                "rollbacks_without_review": rollbacks_without_review,
            },
        }

        return stats

    def save_baseline(
        self,
        post_impl_issues_pct: float = 30.0,
        rollback_rate_pct: float = 10.0,
        design_changes_pct: float = 20.0,
    ) -> None:
        """Save historical baseline (before Pattern 4)"""

        baseline = {
            "period": "Pre-Pattern 4 (historical)",
            "created": datetime.now().isoformat(),
            "post_impl_issues_percent": post_impl_issues_pct,
            "rollback_rate_percent": rollback_rate_pct,
            "design_changes_percent": design_changes_pct,
            "notes": "Estimated from past experience before Pattern 4",
        }

        with open(self.baseline_file, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)

        print(f"[BASELINE] Saved historical baseline to {self.baseline_file}")

    def compare_with_baseline(self) -> Dict:
        """Compare current performance with historical baseline"""

        if not self.baseline_file.exists():
            return {
                "error": "No baseline found",
                "recommendation": "Run with --baseline to set historical baseline first",
            }

        with open(self.baseline_file, "r", encoding="utf-8") as f:
            baseline = json.load(f)

        current = self.calculate_weekly_stats()

        if "error" in current:
            return current

        impls = self.load_implementations(days=7)
        impl_with_review = [i for i in impls if i["design_review_done"]]

        current_bug_rate = current["quality"]["bug_rate_with_review"]
        baseline_bug_rate = baseline["post_impl_issues_percent"]

        improvement = baseline_bug_rate - current_bug_rate
        improvement_pct = (improvement / baseline_bug_rate * 100) if baseline_bug_rate > 0 else 0

        comparison = {
            "baseline": baseline,
            "current": current,
            "improvements": {},
            "verdict": "",
        }

        # Issue prevention comparison
        if improvement > 0:
            comparison["improvements"]["issue_prevention"] = {
                "baseline_bug_rate": baseline_bug_rate,
                "current_bug_rate": current_bug_rate,
                "improvement_percent": improvement_pct,
                "message": f"Issue prevention improved by {improvement_pct:.1f}%",
            }
        else:
            comparison["improvements"]["issue_prevention"] = {
                "baseline_bug_rate": baseline_bug_rate,
                "current_bug_rate": current_bug_rate,
                "improvement_percent": 0,
                "message": "No improvement in issue prevention",
            }

        # Time ROI calculation
        total_review_time = current["design_reviews"]["total_time_minutes"]

        # Estimate bug fix time saved (assume 60 min per bug on average)
        bugs_prevented = (baseline_bug_rate - current_bug_rate) / 100 * len(impl_with_review)
        bug_fix_time_saved = bugs_prevented * 60  # 60 min per bug

        roi = (bug_fix_time_saved / total_review_time * 100) if total_review_time > 0 else 0

        comparison["improvements"]["time_roi"] = {
            "design_review_time": total_review_time,
            "bug_fix_time_saved": bug_fix_time_saved,
            "roi_percent": roi,
            "message": f"ROI: {roi:.0f}% ({bug_fix_time_saved:.0f} min saved / {total_review_time:.0f} min invested)",
        }

        # Verdict
        compliance = current["implementations"]["compliance_rate"]
        if compliance >= 90 and improvement_pct > 20 and roi > 150:
            comparison["verdict"] = "GREEN - Pattern 4 is highly effective, CONTINUE"
        elif compliance >= 70 and improvement_pct > 0:
            comparison["verdict"] = "YELLOW - Some improvement, MONITOR Week 2"
        else:
            comparison["verdict"] = "RED - Not effective, ANALYZE and MODIFY"

        return comparison

    def generate_report(self) -> str:
        """Generate weekly report"""

        stats = self.calculate_weekly_stats()

        if "error" in stats:
            return f"[ERROR] {stats['error']}\n{stats['recommendation']}"

        comparison = self.compare_with_baseline()

        report = []
        report.append("=" * 60)
        report.append("Pattern 4 Weekly Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)

        # Summary
        report.append("\n[SUMMARY]")
        report.append(f"  Total Features: {stats['implementations']['total']}")
        reviews_count = stats["implementations"]["with_review"]
        compliance = stats["implementations"]["compliance_rate"]
        report.append(f"  Design Reviews Done: {reviews_count} ({compliance:.0f}%)")
        report.append(f"  Total Risks Found: {stats['design_reviews']['total_risks_found']}")
        mitigated = stats["design_reviews"]["total_risks_mitigated"]
        mitigation_rate = stats["design_reviews"]["mitigation_rate"]
        report.append(f"  Risks Mitigated: {mitigated} ({mitigation_rate:.0f}%)")

        # Metrics
        report.append("\n[METRICS]")
        report.append("1. Compliance Rate")
        compliance = stats["implementations"]["compliance_rate"]
        status = "[OK]" if compliance >= 90 else "[WARN]" if compliance >= 70 else "[FAIL]"
        report.append(f"   {status} {compliance:.0f}% (target: >90%)")

        report.append("\n2. Risk Detection")
        avg_risks = stats["design_reviews"]["avg_risks_per_review"]
        status = "[OK]" if avg_risks >= 2.0 else "[WARN]" if avg_risks >= 1.5 else "[FAIL]"
        report.append(f"   {status} {avg_risks:.1f} risks per review (target: >2.0)")

        report.append("\n3. Issue Prevention")
        if "error" not in comparison:
            issue_prev = comparison["improvements"]["issue_prevention"]
            status = (
                "[OK]"
                if issue_prev["improvement_percent"] > 20
                else "[WARN]"
                if issue_prev["improvement_percent"] > 0
                else "[FAIL]"
            )
            report.append(f"   {status} {issue_prev['message']}")

        report.append("\n4. Time ROI")
        if "error" not in comparison:
            roi = comparison["improvements"]["time_roi"]
            status = "[OK]" if roi["roi_percent"] > 150 else "[WARN]" if roi["roi_percent"] > 100 else "[FAIL]"
            report.append(f"   {status} {roi['message']}")

        # Verdict
        if "error" not in comparison:
            report.append("\n" + "=" * 60)
            report.append(f"[VERDICT] {comparison['verdict']}")
            report.append("=" * 60)

        return "\n".join(report)


def main():
    """CLI interface"""

    parser = argparse.ArgumentParser(description="Pattern 4 Impact Monitor")

    # Commands
    parser.add_argument("--record-review", action="store_true", help="Record design review")
    parser.add_argument("--record-impl", action="store_true", help="Record implementation")
    parser.add_argument("--baseline", action="store_true", help="Set historical baseline")
    parser.add_argument("--report", action="store_true", help="Generate weekly report")

    # Design review params
    parser.add_argument("--feature", type=str, help="Feature name")
    parser.add_argument("--time", type=float, help="Review time in minutes")
    parser.add_argument("--risks", type=int, help="Number of risks found")
    parser.add_argument("--mitigated", type=int, help="Number of risks mitigated")

    # Implementation params
    parser.add_argument("--bugs", type=int, help="Number of bugs found")
    parser.add_argument("--rollback", type=str, help="Rollback needed (true/false)")
    parser.add_argument("--no-review", action="store_true", help="Implementation without design review")

    # Optional
    parser.add_argument("--notes", type=str, default="", help="Additional notes")

    args = parser.parse_args()

    monitor = Pattern4ImpactMonitor()

    if args.baseline:
        monitor.save_baseline()

    elif args.record_review:
        if not all([args.feature, args.time is not None, args.risks is not None, args.mitigated is not None]):
            print("[ERROR] --record-review requires: --feature, --time, --risks, --mitigated")
            return

        monitor.record_design_review(
            feature=args.feature,
            review_time=args.time,
            risks_found=args.risks,
            risks_mitigated=args.mitigated,
            notes=args.notes,
        )

    elif args.record_impl:
        if not all([args.feature, args.bugs is not None, args.rollback]):
            print("[ERROR] --record-impl requires: --feature, --bugs, --rollback")
            return

        rollback = args.rollback.lower() == "true"

        monitor.record_implementation(
            feature=args.feature,
            bugs_found=args.bugs,
            rollback_needed=rollback,
            design_review_done=not args.no_review,
            notes=args.notes,
        )

    elif args.report:
        report = monitor.generate_report()
        print(report)

        # Save report to file
        report_file = monitor.data_dir / f"report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n[SAVED] Report saved to {report_file}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
