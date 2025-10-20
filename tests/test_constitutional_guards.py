"""
Test Constitutional Guards (Domain-Driven Hexagon Trust 7.6 pattern)

Based on: /sairyss/domain-driven-hexagon guard clauses
Pattern: Fail-fast validation with explicit error types
Validation: TDD-first approach
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestGuardResult:
    """Test GuardResult data structure"""

    def test_guard_result_success(self):
        """Test: GuardResult with succeeded=True"""
        from scripts.constitutional_guards import GuardResult

        result = GuardResult(succeeded=True)
        assert result.succeeded is True
        assert result.message == ""

    def test_guard_result_failure(self):
        """Test: GuardResult with succeeded=False and message"""
        from scripts.constitutional_guards import GuardResult

        result = GuardResult(succeeded=False, message="Validation failed")
        assert result.succeeded is False
        assert result.message == "Validation failed"


class TestConstitutionalGuard:
    """Test constitutional guard clauses (fail-fast validation)"""

    def test_against_null_or_undefined(self):
        """Test: Guard against null/undefined values"""
        from scripts.constitutional_guards import ConstitutionalGuard

        # Should fail for None
        result = ConstitutionalGuard.against_null_or_undefined(None, "test_arg")
        assert result.succeeded is False
        assert "test_arg" in result.message
        assert "required" in result.message.lower()

        # Should succeed for valid value
        result = ConstitutionalGuard.against_null_or_undefined("valid", "test_arg")
        assert result.succeeded is True

    def test_against_empty_string(self):
        """Test: Guard against empty strings"""
        from scripts.constitutional_guards import ConstitutionalGuard

        # Should fail for empty string
        result = ConstitutionalGuard.against_empty_string("", "test_arg")
        assert result.succeeded is False
        assert "test_arg" in result.message

        # Should fail for whitespace only
        result = ConstitutionalGuard.against_empty_string("   ", "test_arg")
        assert result.succeeded is False

        # Should succeed for non-empty string
        result = ConstitutionalGuard.against_empty_string("valid", "test_arg")
        assert result.succeeded is True

    def test_against_implementation_before_tests(self):
        """Test: Article III - TDD validation (implementation must follow tests)"""
        from scripts.constitutional_guards import ConstitutionalGuard, Task

        # Valid: Test before implementation
        tasks = [
            Task(id="1", description="Write test for login", phase=1, order=1, type="test"),
            Task(id="2", description="Implement login", phase=1, order=2, type="implementation"),
        ]
        result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert result.succeeded is True

        # Invalid: Implementation before test
        tasks = [
            Task(id="1", description="Implement login", phase=1, order=1, type="implementation"),
            Task(id="2", description="Write test for login", phase=1, order=2, type="test"),
        ]
        result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert result.succeeded is False
        assert "Article III" in result.message
        assert "1" in result.message  # Task ID

    def test_against_emoji_in_files(self):
        """Test: Article V - Windows cp949 compatibility (no emoji in files)"""
        from scripts.constitutional_guards import ConstitutionalGuard

        temp_dir = Path(tempfile.mkdtemp())

        try:
            # File with emoji
            emoji_file = temp_dir / "emoji.py"
            emoji_file.write_text("# ✅ This has emoji\nprint('hello')", encoding="utf-8")

            result = ConstitutionalGuard.against_emoji_in_files(emoji_file)
            assert result.succeeded is False
            assert "Article V" in result.message
            assert "emoji" in result.message.lower()

            # File without emoji
            clean_file = temp_dir / "clean.py"
            clean_file.write_text("# This is clean\nprint('hello')", encoding="utf-8")

            result = ConstitutionalGuard.against_emoji_in_files(clean_file)
            assert result.succeeded is True

        finally:
            shutil.rmtree(temp_dir)

    def test_against_missing_tests(self):
        """Test: Guard against missing test coverage"""
        from scripts.constitutional_guards import ConstitutionalGuard

        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Project with tests
            (temp_dir / "tests").mkdir()
            (temp_dir / "tests" / "test_example.py").write_text("def test_example(): pass")

            result = ConstitutionalGuard.against_missing_tests(temp_dir)
            assert result.succeeded is True

            # Project without tests
            no_tests_dir = Path(tempfile.mkdtemp())
            (no_tests_dir / "src").mkdir()

            result = ConstitutionalGuard.against_missing_tests(no_tests_dir)
            assert result.succeeded is False
            assert "test" in result.message.lower()

            shutil.rmtree(no_tests_dir)

        finally:
            shutil.rmtree(temp_dir)

    def test_against_hardcoded_secrets(self):
        """Test: Guard against hardcoded secrets in code"""
        from scripts.constitutional_guards import ConstitutionalGuard

        temp_dir = Path(tempfile.mkdtemp())

        try:
            # File with potential secret (using constructed string to avoid detection)
            secret_file = temp_dir / "config.py"
            test_secret = "sk-" + "1234567890abcdef"  # Construct to avoid gitleaks
            secret_file.write_text(f'API_KEY = "{test_secret}"', encoding="utf-8")

            result = ConstitutionalGuard.against_hardcoded_secrets(secret_file)
            assert result.succeeded is False
            assert "secret" in result.message.lower()

            # File with environment variable (safe)
            safe_file = temp_dir / "safe_config.py"
            safe_file.write_text('API_KEY = os.getenv("API_KEY")', encoding="utf-8")

            result = ConstitutionalGuard.against_hardcoded_secrets(safe_file)
            assert result.succeeded is True

        finally:
            shutil.rmtree(temp_dir)


class TestConstitutionalViolationError:
    """Test custom exception for constitutional violations"""

    def test_constitutional_violation_error(self):
        """Test: ConstitutionalViolationError with message"""
        from scripts.constitutional_guards import ConstitutionalViolationError

        with pytest.raises(ConstitutionalViolationError) as exc_info:
            raise ConstitutionalViolationError("Article III violation")

        assert "Article III violation" in str(exc_info.value)


class TestGuardIntegration:
    """Test guard integration with task execution"""

    def test_validate_task_list(self):
        """Test: Validate entire task list before execution"""
        from scripts.constitutional_guards import ConstitutionalGuard, Task

        tasks = [
            Task(id="1", description="Write test", phase=1, order=1, type="test"),
            Task(id="2", description="Implement", phase=1, order=2, type="implementation"),
            Task(id="3", description="🎉 Deploy", phase=2, order=3, type="deployment"),  # Has emoji
        ]

        # Should detect TDD compliance
        tdd_result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert tdd_result.succeeded is True

    def test_guard_combination(self):
        """Test: Multiple guard clauses in sequence"""
        from scripts.constitutional_guards import ConstitutionalGuard

        # Combine multiple guards
        guards = [
            ConstitutionalGuard.against_null_or_undefined("value", "arg"),
            ConstitutionalGuard.against_empty_string("value", "arg"),
        ]

        # All should succeed
        assert all(g.succeeded for g in guards)

    def test_early_exit_on_failure(self):
        """Test: Fail-fast behavior - stop on first violation"""
        from scripts.constitutional_guards import ConstitutionalGuard, ConstitutionalViolationError

        # First guard fails
        result = ConstitutionalGuard.against_null_or_undefined(None, "test")

        if not result.succeeded:
            with pytest.raises(ConstitutionalViolationError):
                raise ConstitutionalViolationError(result.message)
