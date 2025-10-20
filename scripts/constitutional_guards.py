#!/usr/bin/env python3
"""
Constitutional Guards - Domain-Driven Hexagon Trust 7.6 pattern

Based on: /sairyss/domain-driven-hexagon guard clauses
Purpose: Fail-fast validation with explicit error types
Evidence: Hexagon production usage (Trust 7.6)

Pattern:
  Domain-Driven Guard Clauses → Early validation → Explicit errors

Our Implementation:
  Constitutional violations → Guard clauses → ConstitutionalViolationError
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class GuardResult:
    """Result of a guard clause validation"""

    succeeded: bool
    message: str = ""


@dataclass
class Task:
    """Task representation for validation"""

    id: str
    description: str
    phase: int
    order: int
    type: str  # 'test', 'implementation', 'deployment', etc.


class ConstitutionalViolationError(Exception):
    """Raised when a constitutional article is violated"""

    pass


class ConstitutionalGuard:
    """
    Constitutional guard clauses for fail-fast validation

    Based on Domain-Driven Hexagon pattern:
    - Explicit validation before execution
    - Clear error messages with context
    - Fail-fast to prevent invalid states
    """

    @staticmethod
    def against_null_or_undefined(argument, argument_name: str) -> GuardResult:
        """
        Guard against null/undefined values

        Args:
            argument: Value to check
            argument_name: Name of the argument for error message

        Returns:
            GuardResult with success status and optional error message
        """
        if argument is None:
            return GuardResult(succeeded=False, message=f"{argument_name} is required (cannot be None)")
        return GuardResult(succeeded=True)

    @staticmethod
    def against_empty_string(argument: str, argument_name: str) -> GuardResult:
        """
        Guard against empty or whitespace-only strings

        Args:
            argument: String to check
            argument_name: Name of the argument for error message

        Returns:
            GuardResult with success status and optional error message
        """
        if not argument or not argument.strip():
            return GuardResult(succeeded=False, message=f"{argument_name} cannot be empty or whitespace")
        return GuardResult(succeeded=True)

    @staticmethod
    def against_implementation_before_tests(tasks: List[Task]) -> GuardResult:
        """
        Article III: Test-First Development validation

        Ensures implementation tasks are preceded by corresponding test tasks.
        This enforces TDD principles at the task level.

        Args:
            tasks: List of tasks to validate

        Returns:
            GuardResult indicating if TDD order is maintained
        """
        impl_tasks = [t for t in tasks if "implement" in t.description.lower() and t.type == "implementation"]
        test_tasks = [t for t in tasks if t.type == "test"]

        for impl_task in impl_tasks:
            # Find preceding tests in same or earlier phase
            preceding_tests = [
                t
                for t in test_tasks
                if (t.phase < impl_task.phase) or (t.phase == impl_task.phase and t.order < impl_task.order)
            ]

            if not preceding_tests:
                return GuardResult(
                    succeeded=False,
                    message=f"Task {impl_task.id} violates Article III: " f"Implementation before tests (TDD required)",
                )

        return GuardResult(succeeded=True)

    @staticmethod
    def against_emoji_in_files(file_path: Path) -> GuardResult:
        """
        Article V: Windows cp949 compatibility validation

        Ensures files don't contain emoji characters that cause cp949 encoding issues.

        Args:
            file_path: Path to file to check

        Returns:
            GuardResult indicating if file is emoji-free
        """
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map
            "\U0001f700-\U0001f77f"  # alchemical symbols
            "\U0001f780-\U0001f7ff"  # geometric shapes
            "\U0001f800-\U0001f8ff"  # supplemental arrows
            "\U0001f900-\U0001f9ff"  # supplemental symbols
            "\U0001fa00-\U0001fa6f"  # chess symbols
            "\U0001fa70-\U0001faff"  # symbols and pictographs extended
            "\u2600-\u26ff"  # miscellaneous symbols
            "\u2700-\u27bf"  # dingbats
            "]+",
            flags=re.UNICODE,
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if emoji_pattern.search(content):
                return GuardResult(
                    succeeded=False,
                    message=f"{file_path} violates Article V: " f"Contains emoji (Windows cp949 incompatible)",
                )

            return GuardResult(succeeded=True)

        except (OSError, UnicodeDecodeError) as e:
            return GuardResult(succeeded=False, message=f"Error reading {file_path}: {e}")

    @staticmethod
    def against_missing_tests(project_path: Path) -> GuardResult:
        """
        Guard against projects without test coverage

        Args:
            project_path: Path to project root

        Returns:
            GuardResult indicating if tests directory exists
        """
        test_directories = ["tests", "test", "__tests__"]

        for test_dir in test_directories:
            test_path = project_path / test_dir
            if test_path.exists() and test_path.is_dir():
                # Check if there are any test files
                test_files = list(test_path.glob("*.py")) + list(test_path.glob("test_*.py"))
                if test_files:
                    return GuardResult(succeeded=True)

        return GuardResult(
            succeeded=False,
            message=f"No test directory or test files found in {project_path} " f"(expected: tests/, test/, or __tests__/)",
        )

    @staticmethod
    def against_hardcoded_secrets(file_path: Path) -> GuardResult:
        """
        Guard against hardcoded secrets in code

        Detects common secret patterns:
        - API keys (sk-, pk-, etc.)
        - Hardcoded tokens
        - Secret keys

        Args:
            file_path: Path to file to check

        Returns:
            GuardResult indicating if file contains potential secrets
        """
        secret_patterns = [
            r'["\'][a-zA-Z0-9_-]{20,}["\']',  # Long strings (potential tokens)
            r"sk-[a-zA-Z0-9]{20,}",  # Stripe/OpenAI-style secret keys
            r"pk_[a-zA-Z0-9]{20,}",  # Public keys
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',  # API_KEY = "..."
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',  # SECRET_KEY = "..."
            r'token\s*=\s*["\'][^"\']+["\']',  # TOKEN = "..."
        ]

        # Safe patterns (environment variables)
        safe_patterns = [
            r"os\.getenv",
            r"os\.environ",
            r"env\[",
            r"settings\.",
            r"config\.",
        ]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for safe patterns first
            for safe_pattern in safe_patterns:
                if re.search(safe_pattern, content):
                    return GuardResult(succeeded=True)

            # Check for secret patterns
            for secret_pattern in secret_patterns:
                matches = re.findall(secret_pattern, content, re.IGNORECASE)
                if matches:
                    # Filter out common false positives
                    for match in matches:
                        if len(match) > 15 and "example" not in match.lower() and "test" not in match.lower():
                            return GuardResult(
                                succeeded=False,
                                message=f"{file_path} contains potential hardcoded secret. "
                                f"Use environment variables instead (os.getenv())",
                            )

            return GuardResult(succeeded=True)

        except (OSError, UnicodeDecodeError) as e:
            return GuardResult(succeeded=False, message=f"Error reading {file_path}: {e}")


def validate_task_list(tasks: List[Task]) -> None:
    """
    Validate task list against all constitutional guards

    Raises:
        ConstitutionalViolationError: If any guard fails

    Args:
        tasks: List of tasks to validate
    """
    # Article III: Test-First Development
    tdd_result = ConstitutionalGuard.against_implementation_before_tests(tasks)
    if not tdd_result.succeeded:
        raise ConstitutionalViolationError(tdd_result.message)


def validate_file(file_path: Path) -> None:
    """
    Validate file against all constitutional guards

    Raises:
        ConstitutionalViolationError: If any guard fails

    Args:
        file_path: Path to file to validate
    """
    # Article V: No emoji in files
    emoji_result = ConstitutionalGuard.against_emoji_in_files(file_path)
    if not emoji_result.succeeded:
        raise ConstitutionalViolationError(emoji_result.message)

    # Security: No hardcoded secrets
    secret_result = ConstitutionalGuard.against_hardcoded_secrets(file_path)
    if not secret_result.succeeded:
        raise ConstitutionalViolationError(secret_result.message)


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    print("Constitutional Guards - Example Usage")
    print("=" * 50)

    # Example 1: Guard against null
    result = ConstitutionalGuard.against_null_or_undefined(None, "username")
    print(f"\nGuard against null: {result}")

    # Example 2: Guard against empty string
    result = ConstitutionalGuard.against_empty_string("", "password")
    print(f"Guard against empty: {result}")

    # Example 3: TDD validation
    tasks = [
        Task(id="1", description="Implement login", phase=1, order=1, type="implementation"),
        Task(id="2", description="Write test", phase=1, order=2, type="test"),
    ]
    result = ConstitutionalGuard.against_implementation_before_tests(tasks)
    print(f"TDD validation: {result}")

    print("\n" + "=" * 50)
    print("Guards ready for integration with EnhancedTaskExecutor")
