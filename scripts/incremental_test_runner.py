"""Incremental Test Runner - Only test what changed.

This solves the over-testing problem. Instead of running all 784 tests
every time (27+ minutes), we only run tests for changed files.
"""

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple


class IncrementalTestRunner:
    """Run only tests affected by changes."""

    def __init__(self):
        """Initialize incremental test runner."""
        self.cache_dir = Path(".test_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.hash_file = self.cache_dir / "file_hashes.json"
        self.test_map_file = self.cache_dir / "test_mapping.json"
        self.last_hashes = self._load_hashes()
        self.test_mapping = self._load_test_mapping()

    def _load_hashes(self) -> Dict[str, str]:
        """Load cached file hashes."""
        if self.hash_file.exists():
            with open(self.hash_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_hashes(self, hashes: Dict[str, str]) -> None:
        """Save file hashes to cache."""
        with open(self.hash_file, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2)

    def _load_test_mapping(self) -> Dict[str, List[str]]:
        """Load mapping of source files to test files."""
        if self.test_map_file.exists():
            with open(self.test_map_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_test_mapping(self, mapping: Dict[str, List[str]]) -> None:
        """Save test mapping to cache."""
        with open(self.test_map_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2)

    def _hash_file(self, filepath: Path) -> str:
        """Calculate file hash."""
        if not filepath.exists():
            return ""

        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def find_changed_files(self) -> Set[str]:
        """Find files that have changed since last test run."""
        changed = set()
        current_hashes = {}

        # Check Python files
        for filepath in Path("scripts").glob("*.py"):
            current_hash = self._hash_file(filepath)
            current_hashes[str(filepath)] = current_hash

            if str(filepath) not in self.last_hashes:
                changed.add(str(filepath))
                print(f"  [NEW] {filepath}")
            elif self.last_hashes[str(filepath)] != current_hash:
                changed.add(str(filepath))
                print(f"  [CHANGED] {filepath}")

        # Save current hashes
        self._save_hashes(current_hashes)
        self.last_hashes = current_hashes

        return changed

    def map_files_to_tests(self, changed_files: Set[str]) -> Set[str]:
        """Map changed source files to their test files."""
        test_files = set()

        for source_file in changed_files:
            # Direct mapping (e.g., scripts/foo.py -> tests/test_foo.py)
            source_path = Path(source_file)
            test_name = f"test_{source_path.stem}.py"
            test_path = Path("tests") / test_name

            if test_path.exists():
                test_files.add(str(test_path))
                print(f"  {source_file} -> {test_path}")

            # Check cached mapping
            if source_file in self.test_mapping:
                for test_file in self.test_mapping[source_file]:
                    if Path(test_file).exists():
                        test_files.add(test_file)

        return test_files

    def run_tests(self, test_files: Set[str]) -> Tuple[bool, float]:
        """Run only the specified test files."""
        if not test_files:
            print("[INFO] No tests to run (no changes detected)")
            return True, 0.0

        print(f"\n[INFO] Running {len(test_files)} test file(s)...")

        start_time = time.time()
        cmd = [sys.executable, "-m", "pytest"] + list(test_files) + ["-v", "--tb=short"]

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

            # Print summary
            if success:
                print(f"[SUCCESS] Tests passed in {duration:.1f}s")
            else:
                print(f"[FAIL] Some tests failed in {duration:.1f}s")
                # Show failures
                for line in result.stdout.split("\n"):
                    if "FAILED" in line or "ERROR" in line:
                        print(f"  {line}")

            return success, duration

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"[ERROR] Tests timed out after {duration:.1f}s")
            return False, duration

    def run_all_if_needed(self) -> Tuple[bool, float]:
        """Run all tests if critical files changed."""
        # Critical files that affect everything
        critical_files = ["setup.py", "requirements.txt", "pytest.ini", "pyproject.toml"]

        for critical_file in critical_files:
            if Path(critical_file).exists():
                current_hash = self._hash_file(Path(critical_file))
                if critical_file not in self.last_hashes or self.last_hashes[critical_file] != current_hash:
                    print(f"[WARN] Critical file changed: {critical_file}")
                    print("[INFO] Running ALL tests...")
                    return self._run_all_tests()

        return True, 0.0

    def _run_all_tests(self) -> Tuple[bool, float]:
        """Run all tests (fallback)."""
        start_time = time.time()
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=600,  # 10 minute timeout for all tests
            )

            duration = time.time() - start_time
            return result.returncode == 0, duration

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, duration

    def run(self) -> int:
        """Main entry point for incremental testing."""
        print("\n" + "=" * 60)
        print("Incremental Test Runner")
        print("=" * 60)

        # Check for critical file changes
        all_needed, duration = self.run_all_if_needed()
        if duration > 0:
            return 0 if all_needed else 1

        # Find changed files
        print("\n[INFO] Checking for changes...")
        changed_files = self.find_changed_files()

        if not changed_files:
            print("[INFO] No changes detected - skipping tests")
            print("\n[SAVE] Saved approximately 5-10 minutes!")
            return 0

        # Map to test files
        print(f"\n[INFO] Found {len(changed_files)} changed file(s)")
        test_files = self.map_files_to_tests(changed_files)

        # Run tests
        success, duration = self.run_tests(test_files)

        # Show time saved
        full_test_time = 300  # Assume 5 minutes for full suite
        time_saved = full_test_time - duration
        if time_saved > 0:
            print(f"\n[SAVE] Saved approximately {time_saved:.0f} seconds!")

        return 0 if success else 1


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Incremental test runner - only test what changed")
    parser.add_argument("--force-all", action="store_true", help="Force running all tests")
    parser.add_argument("--clear-cache", action="store_true", help="Clear test cache and start fresh")

    args = parser.parse_args()

    runner = IncrementalTestRunner()

    if args.clear_cache:
        import shutil

        if runner.cache_dir.exists():
            shutil.rmtree(runner.cache_dir)
        print("[INFO] Cache cleared")
        runner = IncrementalTestRunner()

    if args.force_all:
        print("[INFO] Force running all tests...")
        success, duration = runner._run_all_tests()
        print(f"[INFO] Completed in {duration:.1f}s")
        return 0 if success else 1

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
