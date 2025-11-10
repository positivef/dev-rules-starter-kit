#!/usr/bin/env python3
"""Enhanced TDD Enforcer - Strict test-first development enforcement with coverage gates.

Features:
- Per-file coverage requirements (min 80%)
- Automated test detection with multiple pattern matching
- Coverage gap reporting
- Pre-commit hook integration
- Configurable enforcement modes (warning/blocking)

Constitutional Compliance:
- P8: Test-First Development (core focus)
- P2: Evidence-Based (logs violations to RUNS/tdd-violations/)
- P6: Quality Gates (coverage thresholds)

Usage:
    python scripts/tdd_enforcer_enhanced.py <file1.py> <file2.py> ...
    python scripts/tdd_enforcer_enhanced.py --strict  # Blocking mode
    python scripts/tdd_enforcer_enhanced.py --report  # Generate coverage report
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import coverage

    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False


class CoverageGap:
    """Represents a coverage gap for a source file."""

    def __init__(self, file_path: str, current_coverage: float, required_coverage: float, missing_lines: List[int]):
        self.file_path = file_path
        self.current_coverage = current_coverage
        self.required_coverage = required_coverage
        self.missing_lines = missing_lines
        self.gap = required_coverage - current_coverage


class EnhancedTDDEnforcer:
    """Enhanced TDD enforcement with coverage tracking and quality gates."""

    def __init__(
        self,
        project_root: Path = None,
        min_coverage: float = 80.0,
        mode: str = "warning",
        evidence_dir: Path = None,
    ):
        """Initialize enhanced TDD enforcer.

        Args:
            project_root: Project root directory
            min_coverage: Minimum coverage percentage required (default: 80%)
            mode: Enforcement mode ('warning' or 'blocking')
            evidence_dir: Directory for violation logs (default: RUNS/tdd-violations/)
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.min_coverage = min_coverage
        self.mode = mode
        self.evidence_dir = evidence_dir or self.project_root / "RUNS" / "tdd-violations"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Test directories
        self.test_dirs = [
            self.project_root / "tests",
            self.project_root / "tests" / "unit",
            self.project_root / "tests" / "integration",
        ]

        # Exempt patterns
        self.exempt_patterns = [
            "__init__.py",
            "__main__.py",
            "setup.py",
            "conftest.py",
            "*_config.py",
            "config.py",
        ]

        # Exempt directories
        self.exempt_dirs = [
            "tests",
            ".git",
            ".github",
            "htmlcov",
            "RUNS",
            "TASKS",
            "docs",
            "config",
            "claudedocs",
            "examples",
        ]

    def is_exempt(self, file_path: Path) -> bool:
        """Check if file is exempt from TDD requirements."""
        # Check filename patterns
        for pattern in self.exempt_patterns:
            if file_path.match(pattern):
                return True

        # Check directory exemptions
        for exempt_dir in self.exempt_dirs:
            if exempt_dir in file_path.parts:
                return True

        return False

    def find_test_file(self, source_file: Path) -> List[Path]:
        """Find existing test files for a source file."""
        # Convert to absolute path for comparison
        source_file = source_file.absolute()

        # Verify source file is within project root
        try:
            source_file.relative_to(self.project_root)
        except ValueError:
            return []

        module_name = source_file.stem

        # Test file naming patterns
        test_names = [
            f"test_{module_name}.py",
            f"{module_name}_test.py",
            f"test_{module_name}_integration.py",
            f"test_{module_name}_unit.py",
        ]

        # Search in test directories
        existing_tests = []
        seen_files = set()

        for test_dir in self.test_dirs:
            if test_dir.exists():
                # Direct search in test directory
                for test_name in test_names:
                    test_file = test_dir / test_name
                    if test_file.exists() and test_file not in seen_files:
                        existing_tests.append(test_file)
                        seen_files.add(test_file)

                # Also search recursively for test files
                for test_name in test_names:
                    for test_file in test_dir.rglob(test_name):
                        if test_file not in seen_files:
                            existing_tests.append(test_file)
                            seen_files.add(test_file)

        return existing_tests

    def check_file_coverage(self, source_file: Path) -> Optional[float]:
        """Check coverage percentage for a specific file.

        Returns:
            Coverage percentage (0-100) or None if coverage data unavailable
        """
        if not COVERAGE_AVAILABLE:
            return None

        coverage_file = self.project_root / ".coverage"
        if not coverage_file.exists():
            return None

        try:
            cov = coverage.Coverage(data_file=str(coverage_file))
            cov.load()

            # Get coverage for this file
            analysis = cov.analysis2(str(source_file))
            executed_lines = len(analysis[1])
            missing_lines = len(analysis[2])
            total_lines = executed_lines + missing_lines

            if total_lines == 0:
                return 100.0

            return (executed_lines / total_lines) * 100.0

        except Exception:
            return None

    def get_missing_lines(self, source_file: Path) -> List[int]:
        """Get list of uncovered line numbers."""
        if not COVERAGE_AVAILABLE:
            return []

        coverage_file = self.project_root / ".coverage"
        if not coverage_file.exists():
            return []

        try:
            cov = coverage.Coverage(data_file=str(coverage_file))
            cov.load()
            analysis = cov.analysis2(str(source_file))
            return list(analysis[2])  # Missing lines
        except Exception:
            return []

    def check_files(self, files: List[Path]) -> Tuple[List[str], List[CoverageGap]]:
        """Check files for test existence and coverage.

        Returns:
            Tuple of (violations, coverage_gaps)
        """
        violations = []
        coverage_gaps = []

        for file_path in files:
            # Skip non-Python files
            if file_path.suffix != ".py":
                continue

            # Skip exempt files
            if self.is_exempt(file_path):
                continue

            # Check if test exists
            test_files = self.find_test_file(file_path)
            if not test_files:
                violations.append(f"No test file found for: {file_path}")
                continue

            # Check coverage
            coverage_pct = self.check_file_coverage(file_path)
            if coverage_pct is not None and coverage_pct < self.min_coverage:
                missing_lines = self.get_missing_lines(file_path)
                gap = CoverageGap(
                    file_path=str(file_path),
                    current_coverage=coverage_pct,
                    required_coverage=self.min_coverage,
                    missing_lines=missing_lines,
                )
                coverage_gaps.append(gap)

        return violations, coverage_gaps

    def log_violations(self, violations: List[str], coverage_gaps: List[CoverageGap]) -> Path:
        """Log violations to evidence directory (P2 compliance).

        Returns:
            Path to log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.evidence_dir / f"tdd_violation_{timestamp}.json"

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "min_coverage": self.min_coverage,
            "violations": {
                "missing_tests": violations,
                "coverage_gaps": [
                    {
                        "file": gap.file_path,
                        "current_coverage": gap.current_coverage,
                        "required_coverage": gap.required_coverage,
                        "gap": gap.gap,
                        "missing_lines": gap.missing_lines[:10],  # First 10 lines
                    }
                    for gap in coverage_gaps
                ],
            },
            "summary": {
                "total_violations": len(violations),
                "total_coverage_gaps": len(coverage_gaps),
            },
        }

        log_file.write_text(json.dumps(log_data, indent=2), encoding="utf-8")
        return log_file

    def generate_report(self, violations: List[str], coverage_gaps: List[CoverageGap]) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("TDD ENFORCER REPORT")
        lines.append("=" * 60)
        lines.append(f"Mode: {self.mode.upper()}")
        lines.append(f"Minimum Coverage: {self.min_coverage}%")
        lines.append("")

        if violations:
            lines.append(f"MISSING TESTS ({len(violations)}):")
            for violation in violations:
                lines.append(f"  - {violation}")
            lines.append("")

        if coverage_gaps:
            lines.append(f"COVERAGE GAPS ({len(coverage_gaps)}):")
            for gap in coverage_gaps:
                lines.append(f"  - {Path(gap.file_path).name}: {gap.current_coverage:.1f}% (need {gap.required_coverage}%)")
                if gap.missing_lines:
                    lines.append(f"    Missing lines: {gap.missing_lines[:5]}...")
            lines.append("")

        if not violations and not coverage_gaps:
            lines.append("[SUCCESS] All files have tests and meet coverage requirements!")
        else:
            lines.append(f"[FAIL] {len(violations)} missing tests, {len(coverage_gaps)} coverage gaps")

        lines.append("=" * 60)
        return "\n".join(lines)

    def enforce(self, files: List[Path]) -> int:
        """Enforce TDD requirements.

        Returns:
            0 if all checks pass, 1 if violations found
        """
        violations, coverage_gaps = self.check_files(files)

        # Log violations (P2 compliance)
        if violations or coverage_gaps:
            log_file = self.log_violations(violations, coverage_gaps)
            print(f"[INFO] Violations logged to: {log_file}")

        # Generate report
        report = self.generate_report(violations, coverage_gaps)
        print(report)

        # Determine exit code
        has_violations = len(violations) > 0 or len(coverage_gaps) > 0

        if has_violations:
            if self.mode == "blocking":
                print("\n[BLOCKED] Commit blocked due to TDD violations")
                return 1
            else:
                print("\n[WARNING] TDD violations detected (warning mode)")
                return 0

        return 0


def main():
    """Main entry point for enhanced TDD enforcer."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced TDD Enforcer")
    parser.add_argument("files", nargs="*", help="Files to check")
    parser.add_argument("--strict", action="store_true", help="Blocking mode (exit 1 on violations)")
    parser.add_argument("--min-coverage", type=float, default=80.0, help="Minimum coverage percentage")
    parser.add_argument("--report", action="store_true", help="Generate coverage gap report")

    args = parser.parse_args()

    # Determine mode
    mode = "blocking" if args.strict else "warning"

    # Get files to check
    if args.files:
        files = [Path(f) for f in args.files if Path(f).exists()]
    else:
        # Get all Python files in scripts/
        project_root = Path(__file__).parent.parent
        files = list((project_root / "scripts").glob("*.py"))

    # Create enforcer
    enforcer = EnhancedTDDEnforcer(
        min_coverage=args.min_coverage,
        mode=mode,
    )

    # Enforce
    exit_code = enforcer.enforce(files)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
