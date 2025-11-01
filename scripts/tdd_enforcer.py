#!/usr/bin/env python3
"""TDD Enforcer - Pre-commit hook to enforce test-first development

Ensures that changed Python files have corresponding test files.
Part of P8 (Test-First Development) constitutional compliance.

Usage:
    python scripts/tdd_enforcer.py <file1.py> <file2.py> ...
"""

import sys
from pathlib import Path
from typing import List, Tuple


class TDDEnforcer:
    """Enforce TDD by checking for test coverage on changed files"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.test_dirs = [
            self.project_root / "tests",
            self.project_root / "tests" / "unit",
            self.project_root / "tests" / "integration",
        ]

        # Files that don't require tests
        self.exempt_patterns = [
            "__init__.py",
            "__main__.py",
            "setup.py",
            "conftest.py",
            "*_config.py",
            "config.py",
        ]

        # Directories that don't require tests
        self.exempt_dirs = [
            "tests",
            ".git",
            ".github",
            "htmlcov",
            "RUNS",
            "TASKS",
            "docs",
            "config",
        ]

    def is_exempt(self, file_path: Path) -> bool:
        """Check if file is exempt from TDD requirements"""
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
        """Find possible test files for a source file

        Returns list of potential test file paths that might exist.
        """
        # Get relative path from project root
        try:
            rel_path = source_file.relative_to(self.project_root)
        except ValueError:
            # File is outside project root
            return []

        # Extract module name
        module_name = source_file.stem

        # Possible test file names
        test_names = [
            f"test_{module_name}.py",
            f"{module_name}_test.py",
            f"test_{module_name}_integration.py",
            f"test_{module_name}_unit.py",
        ]

        # Search in all test directories
        possible_paths = []
        for test_dir in self.test_dirs:
            if test_dir.exists():
                for test_name in test_names:
                    test_file = test_dir / test_name
                    possible_paths.append(test_file)

                # Also check in subdirectories matching source structure
                # e.g., scripts/foo.py -> tests/unit/test_foo.py
                if rel_path.parent.name == "scripts":
                    for test_name in test_names:
                        test_file = test_dir / test_name
                        possible_paths.append(test_file)

        return possible_paths

    def check_file(self, file_path: Path) -> Tuple[bool, str]:
        """Check if a file has tests

        Returns:
            (has_tests: bool, message: str)
        """
        # Skip non-Python files
        if file_path.suffix != ".py":
            return True, f"Skipped (not Python): {file_path}"

        # Skip exempt files
        if self.is_exempt(file_path):
            return True, f"Exempt: {file_path}"

        # Find potential test files
        test_files = self.find_test_file(file_path)

        # Check if any test file exists
        existing_tests = [tf for tf in test_files if tf.exists()]

        if existing_tests:
            return True, f"[OK] Has tests: {file_path} -> {existing_tests[0].name}"
        else:
            # No test file found
            suggestions = "\n    ".join([str(tf) for tf in test_files[:3]])
            return False, (
                f"[WARN] Missing tests: {file_path}\n"
                f"  Expected test file (one of):\n    {suggestions}\n"
                f"  TDD requires tests BEFORE implementation (P8)"
            )

    def check_files(self, file_paths: List[str]) -> Tuple[bool, List[str]]:
        """Check multiple files for test coverage

        Returns:
            (all_pass: bool, messages: List[str])
        """
        messages = []
        all_pass = True

        for file_path_str in file_paths:
            file_path = Path(file_path_str).resolve()

            if not file_path.exists():
                continue

            has_tests, message = self.check_file(file_path)
            messages.append(message)

            if not has_tests:
                all_pass = False

        return all_pass, messages


def main():
    """Main entry point for pre-commit hook"""
    if len(sys.argv) < 2:
        # No files to check
        sys.exit(0)

    enforcer = TDDEnforcer()
    file_paths = sys.argv[1:]

    all_pass, messages = enforcer.check_files(file_paths)

    # Print results
    print("\n=== TDD Enforcer (P8 Test-First Development) ===")
    for message in messages:
        print(message)

    if not all_pass:
        print("\n[WARNING] Some files lack test coverage")
        print("TDD best practice: Write tests BEFORE implementation")
        print("\nOptions:")
        print("  1. Add tests for the changed files")
        print("  2. Skip hook (only if tests will be added in follow-up commit):")
        print("     git commit --no-verify")
        print("\nContinuing commit with warning...")
        # Exit 0 to allow commit (warning only)
        # Change to exit(1) to block commits without tests
        sys.exit(0)
    else:
        print("\n[SUCCESS] All changed files have test coverage!")
        sys.exit(0)


if __name__ == "__main__":
    main()
