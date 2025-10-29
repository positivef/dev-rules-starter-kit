"""Selective Parallel Test Runner - Only parallelize large tests.

This solves the over-parallelization problem. Small tests run faster
sequentially due to parallelization overhead.
"""

import ast
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


class SelectiveParallelRunner:
    """Run tests with intelligent parallelization based on size."""

    # Thresholds for parallelization
    PARALLEL_THRESHOLD = 50  # Min number of tests to parallelize
    LARGE_TEST_THRESHOLD = 100  # Tests this size get more workers

    def __init__(self):
        """Initialize selective parallel runner."""
        self.test_counts: Dict[str, int] = {}
        self.categorized_tests: Dict[str, List[str]] = {
            "small": [],  # < 50 tests
            "medium": [],  # 50-100 tests
            "large": [],  # > 100 tests
        }

    def count_tests_in_file(self, test_file: Path) -> int:
        """Count number of test functions/methods in a file.

        Args:
            test_file: Path to test file.

        Returns:
            Number of test functions.
        """
        if not test_file.exists():
            return 0

        try:
            with open(test_file, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            test_count = 0
            for node in ast.walk(tree):
                # Count test functions
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        test_count += 1
                # Count test methods in classes
                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith("Test"):
                        for method in node.body:
                            if isinstance(method, ast.FunctionDef):
                                if method.name.startswith("test_"):
                                    test_count += 1

            return test_count

        except Exception as e:
            print(f"  [WARN] Could not parse {test_file}: {e}")
            return 0

    def categorize_tests(self) -> None:
        """Categorize test files by size."""
        print("[INFO] Analyzing test file sizes...")

        for test_file in Path("tests").glob("test_*.py"):
            count = self.count_tests_in_file(test_file)
            self.test_counts[str(test_file)] = count

            if count < self.PARALLEL_THRESHOLD:
                self.categorized_tests["small"].append(str(test_file))
                print(f"  [SMALL] {test_file.name}: {count} tests")
            elif count < self.LARGE_TEST_THRESHOLD:
                self.categorized_tests["medium"].append(str(test_file))
                print(f"  [MEDIUM] {test_file.name}: {count} tests")
            else:
                self.categorized_tests["large"].append(str(test_file))
                print(f"  [LARGE] {test_file.name}: {count} tests")

    def run_category(self, category: str, test_files: List[str]) -> Tuple[bool, float]:
        """Run tests in a specific category with appropriate strategy.

        Args:
            category: Test category (small/medium/large).
            test_files: List of test files.

        Returns:
            Tuple of (success, duration).
        """
        if not test_files:
            return True, 0.0

        print(f"\n[INFO] Running {category} tests ({len(test_files)} files)...")

        # Determine parallelization strategy
        if category == "small":
            # Run sequentially - faster for small tests
            parallel_args = []
            print("  Strategy: Sequential (faster for small tests)")
        elif category == "medium":
            # Moderate parallelization
            parallel_args = ["-n", "2"]
            print("  Strategy: 2 parallel workers")
        else:  # large
            # Maximum parallelization
            import multiprocessing

            workers = min(multiprocessing.cpu_count(), 4)
            parallel_args = ["-n", str(workers)]
            print(f"  Strategy: {workers} parallel workers")

        # Build command
        cmd = [sys.executable, "-m", "pytest"] + test_files + parallel_args
        cmd.extend(["-v", "--tb=short"])

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,  # 5 minute timeout
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            if success:
                print(f"  [SUCCESS] {category} tests passed in {duration:.1f}s")
            else:
                print(f"  [FAIL] Some {category} tests failed in {duration:.1f}s")

            return success, duration

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"  [ERROR] {category} tests timed out after {duration:.1f}s")
            return False, duration

    def run(self) -> int:
        """Main entry point for selective parallel testing.

        Returns:
            Exit code (0 for success).
        """
        print("\n" + "=" * 60)
        print("Selective Parallel Test Runner")
        print("=" * 60)

        # Categorize tests
        self.categorize_tests()

        # Show summary
        print("\n[INFO] Test Distribution:")
        print(f"  Small tests (<{self.PARALLEL_THRESHOLD}): {len(self.categorized_tests['small'])} files")
        print(
            f"  Medium tests ({self.PARALLEL_THRESHOLD}-{self.LARGE_TEST_THRESHOLD}): {len(self.categorized_tests['medium'])} files"
        )
        print(f"  Large tests (>{self.LARGE_TEST_THRESHOLD}): {len(self.categorized_tests['large'])} files")

        # Run each category with appropriate strategy
        total_start = time.time()
        all_success = True
        category_times = {}

        for category in ["small", "medium", "large"]:
            success, duration = self.run_category(category, self.categorized_tests[category])
            category_times[category] = duration
            if not success:
                all_success = False

        # Calculate savings
        total_duration = time.time() - total_start
        naive_estimate = sum(self.test_counts.values()) * 0.1  # 0.1s per test estimate
        time_saved = naive_estimate - total_duration

        # Show results
        print("\n" + "=" * 60)
        print("Results Summary")
        print("=" * 60)
        for category, duration in category_times.items():
            if duration > 0:
                print(f"  {category.capitalize()}: {duration:.1f}s")
        print(f"\n  Total: {total_duration:.1f}s")

        if time_saved > 0:
            print(f"  Time saved vs naive parallel: ~{time_saved:.0f}s")
            print(f"  Efficiency gain: {(time_saved/naive_estimate)*100:.0f}%")

        return 0 if all_success else 1

    def recommend_strategy(self) -> None:
        """Recommend optimal test execution strategy."""
        print("\n[INFO] Optimization Recommendations:")

        # Analyze test distribution
        small_count = len(self.categorized_tests["small"])
        large_count = len(self.categorized_tests["large"])

        if small_count > large_count * 2:
            print("  [OK] Many small tests: Sequential execution optimal")
            print("  [OK] Consider combining small test files")

        if large_count > 0:
            print(f"  [OK] {large_count} large test files benefit from parallelization")
            print("  [OK] Consider splitting very large test files (>200 tests)")

        # Check for imbalanced files
        for file, count in self.test_counts.items():
            if count > 200:
                print(f"  [WARN] {Path(file).name} has {count} tests - consider splitting")
            elif count < 5:
                print(f"  [WARN] {Path(file).name} has only {count} tests - consider merging")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Selective parallel test runner - smart parallelization")
    parser.add_argument("--analyze", action="store_true", help="Only analyze test distribution")
    parser.add_argument("--recommend", action="store_true", help="Show optimization recommendations")

    args = parser.parse_args()

    runner = SelectiveParallelRunner()

    if args.analyze:
        runner.categorize_tests()
        runner.recommend_strategy()
        return 0

    if args.recommend:
        runner.categorize_tests()
        runner.recommend_strategy()
        return 0

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
