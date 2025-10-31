"""P14 Degradation Detector - Second-Order Effects monitoring.

Monitors for unintended consequences of changes:
- Override rate degradation
- Quality score degradation
- YAML compliance degradation
- Security issues increase
- Performance degradation

Auto-escalates when thresholds are exceeded.

Usage:
    python scripts/degradation_detector.py --check
    python scripts/degradation_detector.py --monitor
    python scripts/degradation_detector.py --alert
"""

import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "RUNS" / "degradation_state.json"
OVERRIDES_LOG = ROOT / "RUNS" / "overrides.log"


class DegradationDetector:
    """P14: Second-Order Effects detection and monitoring."""

    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()

    def _load_config(self) -> dict:
        """Load degradation settings from .constitution-config.yaml"""
        import yaml

        config_file = ROOT / ".constitution-config.yaml"
        if not config_file.exists():
            return self._default_config()

        try:
            with open(config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("protection", {}).get("degradation_detection", self._default_config())
        except Exception:
            return self._default_config()

    def _default_config(self) -> dict:
        """Default degradation detection configuration"""
        return {
            "enabled": True,
            "metrics": [
                {"name": "override_rate", "threshold": 0.1, "action": "alert"},
                {"name": "quality_score", "threshold": 7.0, "action": "block_pr"},
                {"name": "yaml_compliance", "threshold": 0.3, "action": "alert"},
            ],
        }

    def _load_state(self) -> dict:
        """Load degradation state"""
        if not STATE_FILE.exists():
            return self._initial_state()

        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return self._initial_state()

    def _initial_state(self) -> dict:
        """Initial degradation state"""
        return {
            "last_check": datetime.now().isoformat(),
            "override_history": [],
            "quality_history": [],
            "yaml_compliance_history": [],
            "security_issues_history": [],
            "alerts": [],
        }

    def _save_state(self):
        """Save degradation state"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def check_override_rate(self) -> Dict[str, any]:
        """Check override rate (SKIP_CONSTITUTION usage)"""
        # Read overrides.log
        if not OVERRIDES_LOG.exists():
            return {"rate": 0.0, "count": 0, "threshold": 0.1, "status": "OK"}

        try:
            lines = OVERRIDES_LOG.read_text(encoding="utf-8").splitlines()
            # Simple: count lines in last 7 days
            cutoff = datetime.now() - timedelta(days=7)
            recent_overrides = []

            for line in lines:
                # Parse date from log line (format: YYYY-MM-DD HH:MM:SS)
                try:
                    date_str = line[:19]
                    log_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    if log_date >= cutoff:
                        recent_overrides.append(line)
                except Exception:
                    continue

            # Get total commits in last 7 days
            total_commits = self._count_recent_commits(days=7)
            rate = len(recent_overrides) / total_commits if total_commits > 0 else 0.0

            threshold = next((m["threshold"] for m in self.config["metrics"] if m["name"] == "override_rate"), 0.1)

            return {
                "rate": rate,
                "count": len(recent_overrides),
                "total_commits": total_commits,
                "threshold": threshold,
                "status": "ALERT" if rate > threshold else "OK",
            }

        except Exception as e:
            return {"error": str(e), "status": "ERROR"}

    def _count_recent_commits(self, days: int = 7) -> int:
        """Count commits in last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            result = subprocess.run(
                ["git", "log", f"--since={cutoff_date}", "--oneline"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            return len(result.stdout.splitlines())
        except Exception:
            return 1  # Avoid division by zero

    def check_quality_score(self) -> Dict[str, any]:
        """Check quality score degradation"""
        # Run team_stats_aggregator to get current score
        try:
            result = subprocess.run(
                ["python", "scripts/team_stats_aggregator.py"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse quality_score from output
            # Simple: look for "quality_score: X.X"
            import re

            match = re.search(r"quality[_\s]score[:\s]+(\d+\.\d+)", result.stdout, re.IGNORECASE)
            score = float(match.group(1)) if match else 7.0

            threshold = next((m["threshold"] for m in self.config["metrics"] if m["name"] == "quality_score"), 7.0)

            return {
                "score": score,
                "threshold": threshold,
                "status": "BLOCK" if score < threshold else "OK",
            }

        except Exception as e:
            return {"error": str(e), "status": "ERROR"}

    def check_yaml_compliance(self) -> Dict[str, any]:
        """Check YAML compliance rate"""
        # Count YAML files in TASKS/ vs total tasks
        tasks_dir = ROOT / "TASKS"
        if not tasks_dir.exists():
            return {"rate": 0.0, "threshold": 0.3, "status": "OK"}

        yaml_files = list(tasks_dir.glob("*.yaml")) + list(tasks_dir.glob("*.yml"))
        total_commits = self._count_recent_commits(days=30)  # Last month

        rate = len(yaml_files) / total_commits if total_commits > 0 else 0.0

        threshold = next((m["threshold"] for m in self.config["metrics"] if m["name"] == "yaml_compliance"), 0.3)

        return {
            "rate": rate,
            "yaml_count": len(yaml_files),
            "total_commits": total_commits,
            "threshold": threshold,
            "status": "ALERT" if rate < threshold else "OK",
        }

    def check_security_issues(self) -> Dict[str, any]:
        """Check for security issues increase"""
        # Run gitleaks (if available)
        try:
            result = subprocess.run(
                ["gitleaks", "detect", "--no-git", "-v"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse gitleaks output
            issues_count = result.stdout.count("Finding:")

            return {
                "count": issues_count,
                "threshold": 0,  # Zero tolerance
                "status": "CRITICAL" if issues_count > 0 else "OK",
            }

        except FileNotFoundError:
            # gitleaks not installed
            return {"error": "gitleaks not installed", "status": "SKIP"}
        except Exception as e:
            return {"error": str(e), "status": "ERROR"}

    def monitor(self) -> Dict[str, any]:
        """Run all degradation checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "override_rate": self.check_override_rate(),
            "quality_score": self.check_quality_score(),
            "yaml_compliance": self.check_yaml_compliance(),
            "security_issues": self.check_security_issues(),
        }

        # Track history
        self.state["override_history"].append(
            {
                "date": datetime.now().isoformat()[:10],
                "rate": results["override_rate"].get("rate", 0.0),
            }
        )

        self.state["quality_history"].append(
            {
                "date": datetime.now().isoformat()[:10],
                "score": results["quality_score"].get("score", 0.0),
            }
        )

        self.state["yaml_compliance_history"].append(
            {
                "date": datetime.now().isoformat()[:10],
                "rate": results["yaml_compliance"].get("rate", 0.0),
            }
        )

        self.state["security_issues_history"].append(
            {
                "date": datetime.now().isoformat()[:10],
                "count": results["security_issues"].get("count", 0),
            }
        )

        # Keep only last 30 entries
        for key in ["override_history", "quality_history", "yaml_compliance_history", "security_issues_history"]:
            self.state[key] = self.state[key][-30:]

        self._save_state()

        return results

    def generate_alert(self, results: Dict[str, any]) -> Optional[str]:
        """Generate alert message if thresholds exceeded"""
        alerts = []

        # Override rate alert
        if results["override_rate"]["status"] == "ALERT":
            rate = results["override_rate"]["rate"]
            threshold = results["override_rate"]["threshold"]
            alerts.append(f"[ALERT] Override rate {rate:.1%} > {threshold:.1%}")
            alerts.append(f"  - {results['override_rate']['count']} overrides in last 7 days")
            alerts.append("  - ACTION: Review why SKIP_CONSTITUTION is being used")

        # Quality score alert
        if results["quality_score"]["status"] == "BLOCK":
            score = results["quality_score"]["score"]
            threshold = results["quality_score"]["threshold"]
            alerts.append(f"[BLOCK] Quality score {score} < {threshold}")
            alerts.append("  - ACTION: Block PR until quality improves")

        # YAML compliance alert
        if results["yaml_compliance"]["status"] == "ALERT":
            rate = results["yaml_compliance"]["rate"]
            threshold = results["yaml_compliance"]["threshold"]
            alerts.append(f"[ALERT] YAML compliance {rate:.1%} < {threshold:.1%}")
            alerts.append("  - ACTION: Encourage YAML contract usage for major tasks")

        # Security issues alert
        if results["security_issues"]["status"] == "CRITICAL":
            count = results["security_issues"]["count"]
            alerts.append(f"[CRITICAL] {count} security issues detected")
            alerts.append("  - ACTION: Fix immediately, block deployment")

        if not alerts:
            return None

        alert_msg = "\n".join(
            [
                "=" * 70,
                "P14: DEGRADATION DETECTED",
                "=" * 70,
                "",
                *alerts,
                "",
                "Review INNOVATION_SAFETY_PRINCIPLES.md for mitigation strategies.",
                "",
            ]
        )

        # Save alert
        self.state["alerts"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "message": alert_msg,
            }
        )
        self._save_state()

        return alert_msg

    def dashboard(self) -> str:
        """Generate degradation dashboard"""
        results = self.monitor()

        lines = []
        lines.append("=" * 70)
        lines.append("P14: DEGRADATION DETECTION DASHBOARD")
        lines.append("=" * 70)
        lines.append("")

        # Override Rate
        lines.append("[OVERRIDE RATE]")
        override = results["override_rate"]
        if "error" not in override:
            lines.append(f"  Rate: {override.get('rate', 0):.1%} (threshold: {override.get('threshold', 0.1):.1%})")
            lines.append(f"  Count: {override.get('count', 0)} overrides in last 7 days")
            lines.append(f"  Total commits: {override.get('total_commits', 0)}")
            lines.append(
                f"  Status: {override.get('status', 'UNKNOWN')} {'[WARNING]' if override.get('status') == 'ALERT' else '[CHECKMARK]'}"
            )
        else:
            lines.append(f"  Error: {override['error']}")
        lines.append("")

        # Quality Score
        lines.append("[QUALITY SCORE]")
        quality = results["quality_score"]
        if "error" not in quality:
            lines.append(f"  Score: {quality.get('score', 0)} (threshold: {quality.get('threshold', 7.0)})")
            lines.append(
                f"  Status: {quality.get('status', 'UNKNOWN')} {'[BLOCK]' if quality.get('status') == 'BLOCK' else '[CHECKMARK]'}"
            )
        else:
            lines.append(f"  Error: {quality['error']}")
        lines.append("")

        # YAML Compliance
        lines.append("[YAML COMPLIANCE]")
        yaml_comp = results["yaml_compliance"]
        if "error" not in yaml_comp:
            lines.append(f"  Rate: {yaml_comp.get('rate', 0):.1%} (threshold: {yaml_comp.get('threshold', 0.3):.1%})")
            lines.append(f"  YAML files: {yaml_comp.get('yaml_count', 0)}")
            lines.append(f"  Total commits: {yaml_comp.get('total_commits', 0)}")
            lines.append(
                f"  Status: {yaml_comp.get('status', 'UNKNOWN')} {'[WARNING]' if yaml_comp.get('status') == 'ALERT' else '[CHECKMARK]'}"
            )
        else:
            lines.append(f"  Error: {yaml_comp['error']}")
        lines.append("")

        # Security Issues
        lines.append("[SECURITY ISSUES]")
        security = results["security_issues"]
        if security.get("status") == "SKIP":
            lines.append("  Status: SKIPPED (gitleaks not installed)")
        elif "error" not in security:
            lines.append(f"  Count: {security.get('count', 0)} (threshold: {security.get('threshold', 0)})")
            lines.append(
                f"  Status: {security.get('status', 'UNKNOWN')} {'[CRITICAL]' if security.get('status') == 'CRITICAL' else '[CHECKMARK]'}"
            )
        else:
            lines.append(f"  Error: {security['error']}")
        lines.append("")

        # Alerts
        alert_msg = self.generate_alert(results)
        if alert_msg:
            lines.append(alert_msg)
        else:
            lines.append("[SUCCESS] No degradation detected")
            lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="P14 Degradation Detector")
    parser.add_argument("--check", action="store_true", help="Run all checks")
    parser.add_argument("--monitor", action="store_true", help="Monitor and track history")
    parser.add_argument("--alert", action="store_true", help="Generate alerts if thresholds exceeded")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard")

    args = parser.parse_args()

    detector = DegradationDetector()

    if args.check or args.monitor:
        results = detector.monitor()
        print(json.dumps(results, indent=2))

    if args.alert:
        results = detector.monitor()
        alert = detector.generate_alert(results)
        if alert:
            print(alert)
        else:
            print("[SUCCESS] No alerts")

    if args.dashboard or (not args.check and not args.monitor and not args.alert):
        # Default: show dashboard
        print(detector.dashboard())


if __name__ == "__main__":
    main()
