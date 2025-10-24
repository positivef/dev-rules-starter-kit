"""TDD Enforcer Lite - Coverage Gate for Test-First Development.

Enforces minimum test coverage before commits to ensure code quality.
Integrates with pytest-cov for coverage measurement.

Compliance:
- P2: Evidence-based (measures actual coverage)
- P6: Quality gate (enforces minimum threshold)
- P8: Test-first development
- P10: Windows encoding (UTF-8, no emojis)

Example:
    $ python scripts/tdd_enforcer_lite.py --threshold 85
    $ python scripts/tdd_enforcer_lite.py --strict
    $ python scripts/tdd_enforcer_lite.py --quick
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from scripts.feature_flags import FeatureFlags


class TddEnforcerLite:
    """Lightweight TDD coverage enforcer.

    Enforces minimum test coverage threshold before allowing commits.
    Provides quick mode for development and strict mode for CI/CD.

    Attributes:
        threshold: Minimum coverage percentage (0-100).
        strict: Block commits on failure if True.
        quick: Warning only mode (no blocking).
        evidence_dir: Directory for evidence logs.
    """

    def __init__(
        self,
        threshold: float = 85.0,
        strict: bool = False,
        quick: bool = False,
        evidence_dir: Optional[Path] = None,
    ) -> None:
        """Initialize TDD enforcer.

        Args:
            threshold: Minimum coverage percentage (0-100).
            strict: Block commits if coverage < threshold.
            quick: Warning only, no blocking.
            evidence_dir: Directory to store evidence logs.
        """
        self.threshold = threshold
        self.strict = strict
        self.quick = quick
        self.evidence_dir = evidence_dir or Path("RUNS/evidence")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def run_coverage(self) -> Tuple[bool, Dict[str, float]]:
        """Run pytest with coverage measurement.

        Returns:
            Tuple of (success, coverage_data).
            success: True if tests passed and coverage met threshold.
            coverage_data: Dict with coverage percentages per file.

        Raises:
            RuntimeError: If pytest-cov is not installed.
        """
        try:
            # Run pytest with coverage (with 5-minute timeout to prevent infinite hangs)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "--cov=scripts",
                    "--cov-report=json",
                    "--cov-report=term",
                    "-v",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,  # 5 minutes timeout
            )

            # Check if pytest-cov is installed
            if "No module named" in result.stderr:
                raise RuntimeError("pytest-cov not installed. Install with: pip install pytest-cov")

            # Parse coverage report
            coverage_file = Path("coverage.json")
            if not coverage_file.exists():
                return False, {}

            with open(coverage_file, encoding="utf-8") as f:
                coverage_data = json.load(f)

            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0.0)

            # Tests must pass
            tests_passed = result.returncode == 0

            # Coverage must meet threshold (unless quick mode)
            coverage_met = total_coverage >= self.threshold or self.quick

            success = tests_passed and coverage_met

            return success, {
                "total": total_coverage,
                "threshold": self.threshold,
                "tests_passed": tests_passed,
                "files": coverage_data.get("files", {}),
            }

        except subprocess.TimeoutExpired:
            print("[ERROR] Coverage check timed out after 5 minutes")
            print("[ERROR] This may indicate infinite loops or hanging tests")
            return False, {}
        except FileNotFoundError:
            raise RuntimeError("pytest not found. Install with: pip install pytest pytest-cov")

    def enforce(self) -> int:
        """Enforce coverage gate.

        Returns:
            Exit code (0 = success, 1 = failure).
        """
        print("[INFO] TDD Enforcer Lite - Coverage Gate")
        print(f"[INFO] Threshold: {self.threshold}%")
        print(f"[INFO] Strict mode: {self.strict}")
        print(f"[INFO] Quick mode: {self.quick}")
        print("")

        try:
            success, coverage_data = self.run_coverage()

            total_coverage = coverage_data.get("total", 0.0)
            tests_passed = coverage_data.get("tests_passed", False)

            # Log evidence
            self._log_evidence(success, coverage_data)

            # Print results
            print("")
            print("=" * 60)
            if tests_passed:
                print("[OK] All tests passed")
            else:
                print("[FAIL] Some tests failed")

            print(f"[INFO] Coverage: {total_coverage:.1f}%")

            if total_coverage >= self.threshold:
                print(f"[OK] Coverage meets threshold ({self.threshold}%)")
            else:
                gap = self.threshold - total_coverage
                print(f"[WARN] Coverage below threshold by {gap:.1f}%")

            print("=" * 60)
            print("")

            # Quick mode: always succeed with warning
            if self.quick and not success:
                print("[QUICK MODE] Allowing commit despite failures")
                return 0

            # Strict mode: fail on any issue
            if self.strict and not success:
                print("[STRICT MODE] Blocking commit due to failures")
                return 1

            # Normal mode: warn but allow
            if not success:
                print("[WARN] Quality gate not met, but not blocking")
                return 0

            return 0

        except Exception as e:
            print(f"[ERROR] Failed to run coverage: {e}")
            return 1

    def _log_evidence(self, success: bool, coverage_data: Dict) -> None:
        """Log coverage evidence to RUNS/evidence/.

        Args:
            success: Whether coverage gate passed.
            coverage_data: Coverage measurement data.
        """
        timestamp = datetime.now().isoformat()
        evidence = {
            "timestamp": timestamp,
            "tool": "tdd_enforcer_lite",
            "success": success,
            "threshold": self.threshold,
            "coverage": coverage_data.get("total", 0.0),
            "tests_passed": coverage_data.get("tests_passed", False),
            "strict_mode": self.strict,
            "quick_mode": self.quick,
        }

        evidence_file = self.evidence_dir / f"tdd_coverage_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump(evidence, f, indent=2)

        print(f"[INFO] Evidence logged: {evidence_file}")


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="TDD Enforcer Lite - Coverage Gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/tdd_enforcer_lite.py
  python scripts/tdd_enforcer_lite.py --threshold 90
  python scripts/tdd_enforcer_lite.py --strict
  python scripts/tdd_enforcer_lite.py --quick
        """,
    )

    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=None,
        help="Coverage threshold percentage (default: from feature flags or 85.0)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: block commits on failure",
    )
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick mode: warning only, no blocking",
    )

    args = parser.parse_args()

    # Check feature flags
    flags = FeatureFlags()
    if not flags.is_enabled("tier1_integration.tools.tdd_enforcer"):
        print("[ERROR] tdd_enforcer is disabled by feature flag")
        print("Enable with: python scripts/tier1_cli.py enable tdd_enforcer")
        return 1

    # Get threshold from feature flags if not provided
    threshold = args.threshold
    if threshold is None:
        threshold = flags.get_config("tier1_integration.tools.tdd_enforcer.coverage_threshold")
        if threshold is None:
            threshold = 85.0

    # Get strict mode from feature flags if not provided
    strict = args.strict
    if not strict:
        strict = flags.get_config("tier1_integration.tools.tdd_enforcer.strict_mode")
        if strict is None:
            strict = False

    # Quick mode check
    quick = args.quick
    if quick and not flags.is_enabled("tier1_integration.mitigation.quick_mode.enabled"):
        print("[WARN] Quick mode is disabled by feature flag")
        quick = False

    enforcer = TddEnforcerLite(
        threshold=threshold,
        strict=strict,
        quick=quick,
    )

    return enforcer.enforce()


if __name__ == "__main__":
    sys.exit(main())
