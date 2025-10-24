"""Optimized Test Runner for Tier 1 Integration System.

Provides parallel test execution and test categorization.
"""

import multiprocessing
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class OptimizedTestRunner:
    """Runs tests with optimizations for speed."""

    def __init__(self, parallel: bool = True, workers: Optional[int] = None):
        """Initialize test runner.

        Args:
            parallel: Enable parallel test execution.
            workers: Number of parallel workers (default: CPU count).
        """
        self.parallel = parallel
        self.workers = workers or multiprocessing.cpu_count()

    def categorize_tests(self) -> Dict[str, List[str]]:
        """Categorize tests by type for optimized execution.

        Returns:
            Dictionary mapping test categories to test files.
        """
        test_dir = Path("tests")
        categories = {
            "unit": [],
            "integration": [],
            "slow": [],
            "benchmark": [],
        }

        # Categorize based on file naming patterns
        for test_file in test_dir.glob("test_*.py"):
            file_name = test_file.name

            if "integration" in file_name or "e2e" in file_name:
                categories["integration"].append(str(test_file))
            elif "benchmark" in file_name or "perf" in file_name:
                categories["benchmark"].append(str(test_file))
            elif "slow" in file_name or "stress" in file_name:
                categories["slow"].append(str(test_file))
            else:
                categories["unit"].append(str(test_file))

        return categories

    def run_category(self, category: str, tests: List[str]) -> Tuple[bool, float, str]:
        """Run tests in a specific category.

        Args:
            category: Test category name.
            tests: List of test files.

        Returns:
            Tuple of (success, duration, output).
        """
        if not tests:
            return True, 0.0, f"No {category} tests found"

        start_time = time.time()
        cmd = [sys.executable, "-m", "pytest"] + tests

        # Add category-specific options
        if category == "unit":
            cmd.extend(["-n", str(self.workers)] if self.parallel else [])
            cmd.extend(["--tb=short"])
        elif category == "integration":
            cmd.extend(["-n", "2"] if self.parallel else [])  # Less parallelization
            cmd.extend(["--tb=short"])
        elif category == "slow":
            # Run slow tests sequentially
            cmd.extend(["--tb=short"])
        elif category == "benchmark":
            cmd.extend(["--benchmark-only", "--tb=short"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
            duration = time.time() - start_time
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, duration, output

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, duration, f"Timeout after {duration:.1f}s"

        except Exception as e:
            duration = time.time() - start_time
            return False, duration, str(e)

    def run_quick_tests(self) -> Tuple[bool, float]:
        """Run only quick unit tests for rapid feedback.

        Returns:
            Tuple of (success, duration).
        """
        print("[INFO] Running quick unit tests...")
        categories = self.categorize_tests()
        success, duration, output = self.run_category("unit", categories["unit"])

        if success:
            print(f"[SUCCESS] Quick tests passed in {duration:.1f}s")
        else:
            print(f"[FAIL] Quick tests failed in {duration:.1f}s")
            print(output[-1000:])  # Show last 1000 chars of output

        return success, duration

    def run_all_tests(self) -> Tuple[bool, Dict[str, float]]:
        """Run all tests with optimized execution order.

        Returns:
            Tuple of (overall_success, category_durations).
        """
        print("[INFO] Running optimized test suite...")
        categories = self.categorize_tests()
        results = {}
        overall_success = True

        # Run in optimized order: unit -> integration -> slow -> benchmark
        order = ["unit", "integration", "slow", "benchmark"]

        for category in order:
            if category not in categories:
                continue

            print(f"\n[INFO] Running {category} tests...")
            success, duration, output = self.run_category(category, categories[category])
            results[category] = duration

            if success:
                print(f"[OK] {category} tests passed in {duration:.1f}s")
            else:
                print(f"[FAIL] {category} tests failed in {duration:.1f}s")
                overall_success = False

                # Show errors for failed categories
                if "--tb=short" in output:
                    # Extract failure summary
                    lines = output.split("\n")
                    for i, line in enumerate(lines):
                        if "FAILED" in line or "ERROR" in line:
                            print(line)

        # Print summary
        total_duration = sum(results.values())
        print("\n" + "=" * 60)
        print("Test Execution Summary:")
        print("-" * 60)
        for category, duration in results.items():
            print(f"  {category:12} : {duration:6.1f}s")
        print("-" * 60)
        print(f"  Total        : {total_duration:6.1f}s")
        print("=" * 60)

        return overall_success, results

    def run_specific_test(self, test_path: str) -> Tuple[bool, float]:
        """Run a specific test file or test case.

        Args:
            test_path: Path to test file or specific test.

        Returns:
            Tuple of (success, duration).
        """
        print(f"[INFO] Running specific test: {test_path}")
        start_time = time.time()

        cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60)
            duration = time.time() - start_time
            success = result.returncode == 0

            if success:
                print(f"[SUCCESS] Test passed in {duration:.1f}s")
            else:
                print(f"[FAIL] Test failed in {duration:.1f}s")
                print(result.stdout)

            return success, duration

        except Exception as e:
            duration = time.time() - start_time
            print(f"[ERROR] Test execution failed: {e}")
            return False, duration


def main():
    """CLI for optimized test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Optimized test runner")
    parser.add_argument("--quick", action="store_true", help="Run only quick unit tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--test", help="Run specific test file or test case")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")

    args = parser.parse_args()

    runner = OptimizedTestRunner(parallel=not args.no_parallel, workers=args.workers)

    if args.quick:
        success, duration = runner.run_quick_tests()
        sys.exit(0 if success else 1)

    elif args.all:
        success, results = runner.run_all_tests()
        sys.exit(0 if success else 1)

    elif args.test:
        success, duration = runner.run_specific_test(args.test)
        sys.exit(0 if success else 1)

    else:
        # Default: run quick tests
        success, duration = runner.run_quick_tests()
        print("\n[TIP] Use --all to run all tests or --test <path> for specific tests")
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
