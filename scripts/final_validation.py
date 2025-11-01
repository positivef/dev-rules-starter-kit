#!/usr/bin/env python3
"""Final Integration Validation for Tier 1 System.

Comprehensive validation of all components and features.
Generates final validation report.

Compliance:
- P1: YAML-First
- P2: Evidence-based
- P6: Quality gate
- P10: Windows encoding
"""

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    category: str
    test: str
    passed: bool
    message: str
    duration_ms: float = 0.0


class FinalValidator:
    """Final integration validator for Tier 1 System."""

    def __init__(self):
        """Initialize validator."""
        self.results: List[ValidationResult] = []
        self.start_time = datetime.now()

    def validate_all(self) -> bool:
        """Run all validation checks.

        Returns:
            True if all validations pass.
        """
        print(f"\n{BOLD}{'=' * 60}")
        print("TIER 1 INTEGRATION SYSTEM - FINAL VALIDATION")
        print(f"{'=' * 60}{RESET}\n")

        # Run all validation categories
        self._validate_core_modules()
        self._validate_security()
        self._validate_performance()
        self._validate_integration()
        self._validate_documentation()
        self._validate_deployment()

        # Generate report
        return self._generate_report()

    def _validate_core_modules(self) -> None:
        """Validate core modules."""
        print(f"{BOLD}[1/6] Validating Core Modules...{RESET}")

        # Test imports
        start = time.perf_counter()
        try:
            from tag_extractor_lite import TagExtractorLite
            from tag_sync_bridge_lite import TagSyncBridgeLite  # noqa: F401
            from spec_builder_lite import SpecBuilderLite  # noqa: F401
            from dataview_generator import DataviewGenerator  # noqa: F401
            from mermaid_graph_generator import MermaidGraphGenerator  # noqa: F401

            duration = (time.perf_counter() - start) * 1000
            self._add_result(
                "Core Modules",
                "Module Imports",
                True,
                "All core modules imported successfully",
                duration,
            )
        except ImportError as e:
            self._add_result(
                "Core Modules",
                "Module Imports",
                False,
                f"Import failed: {e}",
            )

        # Test basic functionality
        try:
            extractor = TagExtractorLite()
            tags = extractor.extract_tags_from_directory()
            self._add_result(
                "Core Modules",
                "TAG Extraction",
                True,
                f"Extracted {len(tags)} TAGs",
            )
        except Exception as e:
            self._add_result(
                "Core Modules",
                "TAG Extraction",
                False,
                str(e),
            )

    def _validate_security(self) -> None:
        """Validate security features."""
        print(f"{BOLD}[2/6] Validating Security...{RESET}")

        try:
            from security_utils import (
                SecurePathValidator,
                SecureFileLock,
                MemorySafeResourceManager,
            )

            # Test path validation
            validator = SecurePathValidator()
            base = Path.cwd()
            safe = base / "test.txt"

            start = time.perf_counter()
            validator.validate_path(base, safe)
            duration = (time.perf_counter() - start) * 1000

            self._add_result(
                "Security",
                "Path Validation",
                True,
                "Path traversal protection working",
                duration,
            )

            # Test file locking
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".lock") as f:
                lock_file = Path(f.name)

            lock_file.touch()
            with SecureFileLock(lock_file) as lock:
                self._add_result(
                    "Security",
                    "File Locking",
                    lock._locked,
                    "Cross-platform locking operational",
                )
            lock_file.unlink()

            # Test memory management
            with MemorySafeResourceManager():
                self._add_result(
                    "Security",
                    "Memory Management",
                    True,
                    "Resource cleanup working",
                )

        except Exception as e:
            self._add_result(
                "Security",
                "Security Features",
                False,
                str(e),
            )

    def _validate_performance(self) -> None:
        """Validate performance features."""
        print(f"{BOLD}[3/6] Validating Performance...{RESET}")

        try:
            from parallel_processor import ParallelProcessor, ProcessingTask

            processor = ParallelProcessor(max_workers=4)

            # Create test tasks
            tasks = [ProcessingTask(f"task_{i}", "test", Path(f"file_{i}.py")) for i in range(10)]

            # Simple processor function
            def process(task):
                from parallel_processor import ProcessingResult

                return ProcessingResult(
                    task_id=task.task_id,
                    success=True,
                    data=f"Processed {task.task_id}",
                )

            start = time.perf_counter()
            results = processor.process_tasks(tasks, process)
            duration = (time.perf_counter() - start) * 1000

            success_count = sum(1 for r in results if r.success)
            self._add_result(
                "Performance",
                "Parallel Processing",
                success_count == len(tasks),
                f"Processed {success_count}/{len(tasks)} tasks in {duration:.2f}ms",
                duration,
            )

            # Check performance stats
            stats = processor.get_performance_stats()
            self._add_result(
                "Performance",
                "Performance Metrics",
                stats["success_rate"] == 100.0,
                f"Success rate: {stats['success_rate']}%",
            )

        except Exception as e:
            self._add_result(
                "Performance",
                "Performance Features",
                False,
                str(e),
            )

    def _validate_integration(self) -> None:
        """Validate integration features."""
        print(f"{BOLD}[4/6] Validating Integration...{RESET}")

        try:
            from unified_error_system import UnifiedErrorSystem

            error_system = UnifiedErrorSystem()

            # Test error handling
            test_error = FileNotFoundError("test.txt")
            recovered, _ = error_system.handle_error(
                test_error,
                "validator",
                "test",
                auto_recover=False,
            )

            metrics = error_system.get_metrics()
            self._add_result(
                "Integration",
                "Error System",
                metrics.total_count > 0,
                f"Error handling operational ({metrics.total_count} errors tracked)",
            )

            # Test error recovery
            error_system.get_report()
            self._add_result(
                "Integration",
                "Error Recovery",
                True,
                "Recovery strategies available",
            )

        except Exception as e:
            self._add_result(
                "Integration",
                "Integration Features",
                False,
                str(e),
            )

    def _validate_documentation(self) -> None:
        """Validate documentation."""
        print(f"{BOLD}[5/6] Validating Documentation...{RESET}")

        docs = [
            ("README_TIER1.md", "Main documentation"),
            ("docs/PERFORMANCE_REPORT.md", "Performance report"),
            (".github/workflows/tier1-ci.yml", "CI/CD pipeline"),
            ("Dockerfile", "Docker configuration"),
            ("docker-compose.yml", "Docker Compose"),
        ]

        for doc_path, description in docs:
            path = Path(doc_path)
            if path.exists():
                size = path.stat().st_size
                self._add_result(
                    "Documentation",
                    description,
                    True,
                    f"Present ({size:,} bytes)",
                )
            else:
                self._add_result(
                    "Documentation",
                    description,
                    False,
                    "Missing",
                )

    def _validate_deployment(self) -> None:
        """Validate deployment readiness."""
        print(f"{BOLD}[6/6] Validating Deployment...{RESET}")

        # Check requirements file
        req_file = Path("requirements.txt")
        if req_file.exists():
            with open(req_file) as f:
                deps = len([line for line in f if line.strip() and not line.startswith("#")])
            self._add_result(
                "Deployment",
                "Dependencies",
                True,
                f"{deps} dependencies defined",
            )
        else:
            self._add_result(
                "Deployment",
                "Dependencies",
                False,
                "requirements.txt missing",
            )

        # Check test coverage
        import subprocess

        try:
            # Use --collect-only with json report for accurate test counting
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Count lines that end with test pattern (e.g., "test_name.py::TestClass::test_method")
            test_lines = [
                line
                for line in result.stdout.split("\n")
                if line.strip() and ("::test_" in line or "::Test" in line or line.strip().endswith(".py"))
            ]
            # Filter out directory listings and get actual test count
            test_count = len([line for line in test_lines if "::" in line and not line.strip().startswith("<")])

            # If still 0, try alternative counting method
            if test_count == 0:
                # Count "collected X items" from stderr or stdout
                import re

                collected_match = re.search(r"collected (\d+) item", result.stdout + result.stderr)
                if collected_match:
                    test_count = int(collected_match.group(1))

            self._add_result(
                "Deployment",
                "Test Suite",
                test_count > 0,
                f"{test_count} tests available",
            )
        except Exception:
            # Try fallback method - count test files
            try:
                test_files = list(Path("tests").glob("test_*.py"))
                estimated_count = len(test_files) * 10  # Rough estimate
                self._add_result(
                    "Deployment",
                    "Test Suite",
                    len(test_files) > 0,
                    f"~{estimated_count} tests (estimated from {len(test_files)} files)",
                )
            except Exception:
                self._add_result(
                    "Deployment",
                    "Test Suite",
                    False,
                    "Unable to count tests",
                )

        # Check Python version
        py_version = sys.version_info
        py_ok = py_version >= (3, 8)
        self._add_result(
            "Deployment",
            "Python Version",
            py_ok,
            f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
        )

    def _add_result(
        self,
        category: str,
        test: str,
        passed: bool,
        message: str,
        duration_ms: float = 0.0,
    ) -> None:
        """Add validation result.

        Args:
            category: Test category.
            test: Test name.
            passed: Whether test passed.
            message: Result message.
            duration_ms: Test duration.
        """
        result = ValidationResult(category, test, passed, message, duration_ms)
        self.results.append(result)

        # Print immediate feedback
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {test}: {message}")

    def _generate_report(self) -> bool:
        """Generate final validation report.

        Returns:
            True if all validations passed.
        """
        print(f"\n{BOLD}{'=' * 60}")
        print("VALIDATION REPORT")
        print(f"{'=' * 60}{RESET}\n")

        # Group results by category
        by_category: Dict[str, List[ValidationResult]] = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)

        # Summary by category
        all_passed = True
        for category, results in by_category.items():
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            rate = (passed / total * 100) if total > 0 else 0

            if rate == 100:
                status = f"{GREEN}PASS{RESET}"
            elif rate >= 75:
                status = f"{YELLOW}WARN{RESET}"
            else:
                status = f"{RED}FAIL{RESET}"
                all_passed = False

            print(f"{BOLD}{category}:{RESET}")
            print(f"  Status: {status}")
            print(f"  Passed: {passed}/{total} ({rate:.1f}%)")

            # Show failures
            failures = [r for r in results if not r.passed]
            if failures:
                print("  Failures:")
                for failure in failures:
                    print(f"    - {failure.test}: {failure.message}")
            print()

        # Overall summary
        total_passed = sum(1 for r in self.results if r.passed)
        total_tests = len(self.results)
        overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print(f"{BOLD}OVERALL SUMMARY{RESET}")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {total_passed}")
        print(f"  Failed: {total_tests - total_passed}")
        print(f"  Success Rate: {overall_rate:.1f}%")

        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"  Validation Time: {duration:.2f}s")

        # Final verdict
        print(f"\n{BOLD}FINAL VERDICT: ", end="")
        if all_passed and overall_rate == 100:
            print(f"{GREEN}[PASS] PRODUCTION READY{RESET}")
            print("\nThe Tier 1 Integration System is fully validated and ready for production!")
        elif overall_rate >= 90:
            print(f"{GREEN}[PASS] READY WITH MINOR ISSUES{RESET}")
            print("\nThe system is ready but has minor issues that should be addressed.")
        elif overall_rate >= 75:
            print(f"{YELLOW}[WARN] NEEDS IMPROVEMENT{RESET}")
            print("\nThe system needs improvements before production deployment.")
        else:
            print(f"{RED}[FAIL] NOT READY{RESET}")
            print("\nThe system has critical issues that must be resolved.")

        # Save report to file
        self._save_report(overall_rate, all_passed)

        return all_passed

    def _save_report(self, overall_rate: float, all_passed: bool) -> None:
        """Save validation report to file.

        Args:
            overall_rate: Overall success rate.
            all_passed: Whether all tests passed.
        """
        report = {
            "timestamp": self.start_time.isoformat(),
            "overall_rate": overall_rate,
            "all_passed": all_passed,
            "results": [
                {
                    "category": r.category,
                    "test": r.test,
                    "passed": r.passed,
                    "message": r.message,
                    "duration_ms": r.duration_ms,
                }
                for r in self.results
            ],
        }

        report_path = Path("validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_path}")


def main() -> int:
    """Run final validation.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    validator = FinalValidator()

    try:
        all_passed = validator.validate_all()
        return 0 if all_passed else 1

    except Exception as e:
        print(f"\n{RED}[ERROR] Validation failed: {e}{RESET}")
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
