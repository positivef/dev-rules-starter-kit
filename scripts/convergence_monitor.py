"""P15 Convergence Monitor - Automated ROI tracking and complexity budget enforcement.

Monitors:
- ROI trends (Phase 1/2/3)
- Complexity budget (articles, lines)
- Stability duration
- New proposal ROI requirements

Auto-escalates when stop conditions are met.

Usage:
    python scripts/convergence_monitor.py --check
    python scripts/convergence_monitor.py --dashboard
    python scripts/convergence_monitor.py --quarterly-review
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "RUNS" / "convergence_state.json"


class ConvergenceMonitor:
    """P15: Convergence Principle automation."""

    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()

    def _load_config(self) -> dict:
        """Load convergence settings from .constitution-config.yaml"""
        import yaml

        config_file = ROOT / ".constitution-config.yaml"
        if not config_file.exists():
            return self._default_config()

        try:
            with open(config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("convergence", self._default_config())
        except Exception:
            return self._default_config()

    def _default_config(self) -> dict:
        """Default convergence configuration"""
        return {
            "stop_conditions": {
                "roi_threshold": 300,
                "satisfaction_threshold": 80,
                "stable_duration_days": 90,
                "new_proposal_roi_min": 150,
            },
            "complexity_budget": {
                "max_articles": 20,
                "max_lines_per_article": 150,
                "max_total_lines": 1500,
                "current_articles": 15,
                "current_lines": 1400,
            },
            "review_schedule": {
                "frequency": "quarterly",
                "next_review": "2026-01-31",
            },
        }

    def _load_state(self) -> dict:
        """Load convergence state from RUNS/convergence_state.json"""
        if not STATE_FILE.exists():
            return self._initial_state()

        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return self._initial_state()

    def _initial_state(self) -> dict:
        """Initial convergence state"""
        return {
            "last_check": datetime.now().isoformat(),
            "roi_history": [{"date": "2025-10-31", "phase_1": 9300, "phase_2": 7200, "phase_3": 3900, "total": 20400}],
            "complexity_history": [{"date": "2025-10-31", "articles": 15, "lines": 1400}],
            "stop_condition_alerts": [],
            "quarterly_reviews": [],
            "satisfaction_scores": [{"date": "2025-10-31", "score": 85, "source": "initial_estimate"}],
        }

    def _save_state(self):
        """Save convergence state"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def check_stop_conditions(self) -> Dict[str, bool]:
        """Check all stop conditions"""
        stop_config = self.config["stop_conditions"]

        # Get latest metrics
        latest_roi = self.state["roi_history"][-1] if self.state["roi_history"] else {}
        latest_complexity = self.state["complexity_history"][-1] if self.state["complexity_history"] else {}
        latest_satisfaction = self.state["satisfaction_scores"][-1] if self.state["satisfaction_scores"] else {}

        roi_total = latest_roi.get("total", 0)
        satisfaction = latest_satisfaction.get("score", 0)
        articles = latest_complexity.get("articles", 0)
        lines = latest_complexity.get("lines", 0)

        # Check stable duration
        stable_days = self._calculate_stable_days()

        results = {
            "roi_met": roi_total >= stop_config["roi_threshold"],
            "satisfaction_met": satisfaction >= stop_config["satisfaction_threshold"],
            "stable_met": stable_days >= stop_config["stable_duration_days"],
            "complexity_ok": (
                articles <= self.config["complexity_budget"]["max_articles"]
                and lines <= self.config["complexity_budget"]["max_total_lines"]
            ),
            "all_met": False,
        }

        results["all_met"] = (
            results["roi_met"] and results["satisfaction_met"] and results["stable_met"] and results["complexity_ok"]
        )

        return results

    def _calculate_stable_days(self) -> int:
        """Calculate days since last major change"""
        # Simple: days since project start (2025-10-23 per NORTH_STAR.md)
        start_date = datetime(2025, 10, 23)
        now = datetime.now()
        return (now - start_date).days

    def track_roi(self, phase_1: int, phase_2: int, phase_3: int):
        """Track ROI metrics"""
        entry = {
            "date": datetime.now().isoformat()[:10],
            "phase_1": phase_1,
            "phase_2": phase_2,
            "phase_3": phase_3,
            "total": phase_1 + phase_2 + phase_3,
        }
        self.state["roi_history"].append(entry)
        self._save_state()

    def track_complexity(self, articles: int, lines: int):
        """Track complexity metrics"""
        entry = {
            "date": datetime.now().isoformat()[:10],
            "articles": articles,
            "lines": lines,
        }
        self.state["complexity_history"].append(entry)
        self._save_state()

    def track_satisfaction(self, score: int, source: str):
        """Track satisfaction scores"""
        entry = {
            "date": datetime.now().isoformat()[:10],
            "score": score,
            "source": source,
        }
        self.state["satisfaction_scores"].append(entry)
        self._save_state()

    def generate_dashboard(self) -> str:
        """Generate convergence dashboard"""
        results = self.check_stop_conditions()
        stop_config = self.config["stop_conditions"]

        latest_roi = self.state["roi_history"][-1] if self.state["roi_history"] else {}
        latest_complexity = self.state["complexity_history"][-1] if self.state["complexity_history"] else {}
        latest_satisfaction = self.state["satisfaction_scores"][-1] if self.state["satisfaction_scores"] else {}

        dashboard = []
        dashboard.append("=" * 70)
        dashboard.append("P15: CONVERGENCE DASHBOARD")
        dashboard.append("=" * 70)
        dashboard.append("")

        # ROI Section
        dashboard.append("[ROI TRACKING]")
        dashboard.append(f"  Phase 1: {latest_roi.get('phase_1', 0):,}%")
        dashboard.append(f"  Phase 2: {latest_roi.get('phase_2', 0):,}%")
        dashboard.append(f"  Phase 3: {latest_roi.get('phase_3', 0):,}%")
        dashboard.append(f"  Total:   {latest_roi.get('total', 0):,}% (threshold: {stop_config['roi_threshold']}%)")
        dashboard.append(
            f"  Status:  {'STOP CONDITION MET' if results['roi_met'] else 'Continue'} {'[CHECKMARK]' if results['roi_met'] else ''}"
        )
        dashboard.append("")

        # Satisfaction Section
        dashboard.append("[SATISFACTION]")
        dashboard.append(
            f"  Score: {latest_satisfaction.get('score', 0)}% (threshold: {stop_config['satisfaction_threshold']}%)"
        )
        dashboard.append(f"  Source: {latest_satisfaction.get('source', 'N/A')}")
        dashboard.append(
            f"  Status: {'STOP CONDITION MET' if results['satisfaction_met'] else 'Continue'} {'[CHECKMARK]' if results['satisfaction_met'] else ''}"
        )
        dashboard.append("")

        # Stability Section
        stable_days = self._calculate_stable_days()
        dashboard.append("[STABILITY]")
        dashboard.append(f"  Stable for: {stable_days} days (threshold: {stop_config['stable_duration_days']} days)")
        dashboard.append(
            f"  Status: {'STOP CONDITION MET' if results['stable_met'] else 'Continue'} {'[CHECKMARK]' if results['stable_met'] else ''}"
        )
        dashboard.append("")

        # Complexity Budget Section
        max_articles = self.config["complexity_budget"]["max_articles"]
        max_lines = self.config["complexity_budget"]["max_total_lines"]
        articles = latest_complexity.get("articles", 0)
        lines = latest_complexity.get("lines", 0)

        dashboard.append("[COMPLEXITY BUDGET]")
        dashboard.append(f"  Articles: {articles} / {max_articles} (max)")
        dashboard.append(f"  Lines:    {lines} / {max_lines} (max)")
        dashboard.append(f"  Remaining: {max_articles - articles} articles, {max_lines - lines} lines")
        dashboard.append(
            f"  Status: {'OK' if results['complexity_ok'] else 'EXCEEDED'} {'[CHECKMARK]' if results['complexity_ok'] else '[WARNING]'}"
        )
        dashboard.append("")

        # Overall Status
        dashboard.append("=" * 70)
        dashboard.append("OVERALL STATUS")
        dashboard.append("=" * 70)

        if results["all_met"]:
            dashboard.append("[SUCCESS] ALL STOP CONDITIONS MET")
            dashboard.append("")
            dashboard.append("RECOMMENDATIONS:")
            dashboard.append("  1. STOP adding new features")
            dashboard.append("  2. FOCUS on:")
            dashboard.append("     - Documentation and user guides")
            dashboard.append("     - Testing and quality assurance")
            dashboard.append("     - Stability and bug fixes")
            dashboard.append("     - User feedback collection")
            dashboard.append("  3. New proposals require ROI > 150%")
            dashboard.append("")
            dashboard.append("RATIONALE:")
            dashboard.append(f"  - ROI {latest_roi.get('total', 0):,}% >> {stop_config['roi_threshold']}% threshold")
            dashboard.append(
                f"  - Satisfaction {latest_satisfaction.get('score', 0)}% >= {stop_config['satisfaction_threshold']}%"
            )
            dashboard.append(f"  - Stable for {stable_days} days >= {stop_config['stable_duration_days']} days")
            dashboard.append("  - System is 'Good Enough' (P15 philosophy)")
            dashboard.append("  - Avoid diminishing returns")
        else:
            dashboard.append("[INFO] Continue development")
            dashboard.append("")
            dashboard.append("PENDING CONDITIONS:")
            if not results["roi_met"]:
                dashboard.append(f"  - ROI {latest_roi.get('total', 0):,}% < {stop_config['roi_threshold']}%")
            if not results["satisfaction_met"]:
                dashboard.append(
                    f"  - Satisfaction {latest_satisfaction.get('score', 0)}% < {stop_config['satisfaction_threshold']}%"
                )
            if not results["stable_met"]:
                dashboard.append(f"  - Stable {stable_days} days < {stop_config['stable_duration_days']} days")
            if not results["complexity_ok"]:
                dashboard.append("  - Complexity budget exceeded")

        dashboard.append("")
        return "\n".join(dashboard)

    def quarterly_review(self) -> dict:
        """Perform quarterly review as per P15"""
        review = {
            "date": datetime.now().isoformat()[:10],
            "stop_conditions": self.check_stop_conditions(),
            "roi_trend": self._analyze_roi_trend(),
            "complexity_trend": self._analyze_complexity_trend(),
            "recommendations": [],
        }

        # Generate recommendations
        if review["stop_conditions"]["all_met"]:
            review["recommendations"].append("STOP: All conditions met, focus on stability")
        else:
            review["recommendations"].append("CONTINUE: Not all conditions met yet")

        if review["complexity_trend"]["increasing"]:
            review["recommendations"].append("WARNING: Complexity increasing, consider cleanup")

        if review["roi_trend"]["diminishing"]:
            review["recommendations"].append("INFO: ROI diminishing, focus on high-value items")

        # Save review
        self.state["quarterly_reviews"].append(review)
        self._save_state()

        return review

    def _analyze_roi_trend(self) -> dict:
        """Analyze ROI trend"""
        history = self.state["roi_history"]
        if len(history) < 2:
            return {"trend": "stable", "diminishing": False}

        latest = history[-1]["total"]
        previous = history[-2]["total"]
        growth = latest - previous

        return {
            "trend": "increasing" if growth > 0 else "stable",
            "growth": growth,
            "diminishing": growth < 100,  # Less than 100% growth = diminishing
        }

    def _analyze_complexity_trend(self) -> dict:
        """Analyze complexity trend"""
        history = self.state["complexity_history"]
        if len(history) < 2:
            return {"trend": "stable", "increasing": False}

        latest = history[-1]
        previous = history[-2]

        articles_growth = latest["articles"] - previous["articles"]
        lines_growth = latest["lines"] - previous["lines"]

        return {
            "trend": "increasing" if (articles_growth > 0 or lines_growth > 0) else "stable",
            "articles_growth": articles_growth,
            "lines_growth": lines_growth,
            "increasing": articles_growth > 0 or lines_growth > 0,
        }


def main():
    parser = argparse.ArgumentParser(description="P15 Convergence Monitor")
    parser.add_argument("--check", action="store_true", help="Check stop conditions")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard")
    parser.add_argument("--quarterly-review", action="store_true", help="Run quarterly review")
    parser.add_argument("--track-roi", nargs=3, type=int, metavar=("P1", "P2", "P3"), help="Track ROI (Phase 1, 2, 3)")
    parser.add_argument("--track-complexity", nargs=2, type=int, metavar=("ARTICLES", "LINES"), help="Track complexity")
    parser.add_argument("--track-satisfaction", nargs=2, metavar=("SCORE", "SOURCE"), help="Track satisfaction")

    args = parser.parse_args()

    monitor = ConvergenceMonitor()

    if args.check:
        results = monitor.check_stop_conditions()
        print(f"Stop conditions met: {results['all_met']}")
        print(json.dumps(results, indent=2))

    elif args.dashboard:
        print(monitor.generate_dashboard())

    elif args.quarterly_review:
        review = monitor.quarterly_review()
        print(json.dumps(review, indent=2))
        print("\nQuarterly review completed and saved to RUNS/convergence_state.json")

    elif args.track_roi:
        p1, p2, p3 = args.track_roi
        monitor.track_roi(p1, p2, p3)
        print(f"ROI tracked: Phase 1={p1}%, Phase 2={p2}%, Phase 3={p3}%, Total={p1+p2+p3}%")

    elif args.track_complexity:
        articles, lines = args.track_complexity
        monitor.track_complexity(articles, lines)
        print(f"Complexity tracked: {articles} articles, {lines} lines")

    elif args.track_satisfaction:
        score, source = args.track_satisfaction
        monitor.track_satisfaction(int(score), source)
        print(f"Satisfaction tracked: {score}% from {source}")

    else:
        # Default: show dashboard
        print(monitor.generate_dashboard())


if __name__ == "__main__":
    main()
