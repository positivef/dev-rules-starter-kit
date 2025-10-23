#!/usr/bin/env python3
"""
Tests for Enhanced Error Handler

Purpose: Verify user-friendly error messages

Constitutional Compliance:
- [P3] Test-First Development
- [P6] Observability
- [P10] Windows UTF-8 (ASCII-only output)
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from error_handler import (
    EnhancedError,
    ErrorSeverity,
    ErrorCatalog,
    format_error_for_user,
)


class TestEnhancedError:
    """Test EnhancedError functionality"""

    def test_basic_error(self):
        """Test creating a basic error"""
        error = EnhancedError(message="Test error", severity=ErrorSeverity.ERROR)

        assert error.message == "Test error"
        assert error.severity == ErrorSeverity.ERROR
        assert error.suggestion is None

    def test_error_with_suggestion(self):
        """Test error with suggestion"""
        error = EnhancedError(message="Command failed", severity=ErrorSeverity.ERROR, suggestion="Try running with sudo")

        assert error.suggestion == "Try running with sudo"

    def test_error_format_basic(self):
        """Test basic error formatting"""
        error = EnhancedError(message="Test error", severity=ErrorSeverity.ERROR)

        formatted = error.format()

        assert "[ERROR] Test error" in formatted
        assert "[SUGGESTION]" not in formatted  # No suggestion provided

    def test_error_format_with_suggestion(self):
        """Test formatting with suggestion"""
        error = EnhancedError(message="Test error", severity=ErrorSeverity.ERROR, suggestion="Try this fix")

        formatted = error.format()

        assert "[ERROR] Test error" in formatted
        assert "[SUGGESTION] Try this fix" in formatted

    def test_error_format_with_details(self):
        """Test formatting with details"""
        error = EnhancedError(
            message="Test error",
            severity=ErrorSeverity.ERROR,
            details={"file": "test.py", "line": 42},
        )

        formatted = error.format(include_details=True)

        assert "[DETAILS]" in formatted
        assert "file: test.py" in formatted
        assert "line: 42" in formatted

    def test_error_format_without_details(self):
        """Test formatting without details"""
        error = EnhancedError(
            message="Test error",
            severity=ErrorSeverity.ERROR,
            details={"file": "test.py"},
        )

        formatted = error.format(include_details=False)

        assert "[DETAILS]" not in formatted
        assert "file: test.py" not in formatted


class TestErrorCatalog:
    """Test error catalog functionality"""

    def test_command_not_allowed(self):
        """Test command not allowed error"""
        error = ErrorCatalog.command_not_allowed("dangerous_cmd")

        assert "dangerous_cmd" in error.message
        assert "ALLOWED_CMDS" in error.suggestion
        assert error.severity == ErrorSeverity.ERROR

        formatted = error.format()
        assert "[ERROR]" in formatted
        assert "SUGGESTION" in formatted

    def test_file_not_found(self):
        """Test file not found error"""
        error = ErrorCatalog.file_not_found("nonexistent.txt")

        assert "nonexistent.txt" in error.message
        assert "Check if the file exists" in error.suggestion
        assert error.severity == ErrorSeverity.ERROR

    def test_yaml_parse_error(self):
        """Test YAML parse error"""
        original_error = ValueError("Invalid YAML")
        error = ErrorCatalog.yaml_parse_error("bad.yaml", original_error)

        assert "bad.yaml" in error.message
        assert "YAML syntax" in error.suggestion
        assert error.original_error == original_error

    def test_missing_required_field(self):
        """Test missing required field error"""
        error = ErrorCatalog.missing_required_field("task_id", "YAML contract")

        assert "task_id" in error.message
        assert "YAML contract" in error.message
        assert "Add the required field" in error.suggestion

    def test_command_failed(self):
        """Test command failed error"""
        error = ErrorCatalog.command_failed("pytest", 1, "FAILED tests/test_foo.py")

        assert "pytest" in error.message
        assert "exit code 1" in error.message
        assert "Troubleshooting steps" in error.suggestion
        assert "FAILED tests/test_foo.py" in error.details["stderr_preview"]

    def test_budget_exceeded(self):
        """Test budget exceeded error"""
        error = ErrorCatalog.budget_exceeded(15.0, 10.0)

        assert "$15.00" in error.message
        assert "$10.00" in error.message
        assert "Increase budget" in error.suggestion
        assert error.details["overage"] == 5.0

    def test_human_approval_required(self):
        """Test human approval required warning"""
        error = ErrorCatalog.human_approval_required("abc123", "TASK-01")

        assert "Human approval" in error.message
        assert error.severity == ErrorSeverity.WARNING
        assert "abc123" in error.suggestion
        assert "TASK-01" in error.suggestion

    def test_compression_failed(self):
        """Test compression failed warning"""
        original_error = RuntimeError("Compression error")
        error = ErrorCatalog.compression_failed(original_error)

        assert error.severity == ErrorSeverity.WARNING
        assert "non-critical" in error.suggestion
        assert error.original_error == original_error


class TestFormatErrorForUser:
    """Test generic error formatting"""

    def test_format_generic_exception(self):
        """Test formatting a generic exception"""
        try:
            raise ValueError("Something went wrong")
        except ValueError as e:
            formatted = format_error_for_user(e)

            assert "[ERROR]" in formatted
            assert "ValueError" in formatted
            assert "Something went wrong" in formatted

    def test_format_with_context(self):
        """Test formatting with context"""
        try:
            raise RuntimeError("Failed")
        except RuntimeError as e:
            formatted = format_error_for_user(e, context="During file processing")

            assert "[CONTEXT] During file processing" in formatted


class TestASCIICompliance:
    """Test that all error messages use ASCII-only characters (P10)"""

    def test_enhanced_error_ascii_only(self):
        """Test EnhancedError uses ASCII-only"""
        error = EnhancedError(
            message="Test error message",
            severity=ErrorSeverity.ERROR,
            suggestion="Fix suggestion",
            details={"key": "value"},
        )

        formatted = error.format()

        # All characters should be ASCII (< 128) except newlines
        assert all(ord(c) < 128 or c in ["\n"] for c in formatted)

    def test_catalog_errors_ascii_only(self):
        """Test all catalog errors use ASCII-only"""
        errors = [
            ErrorCatalog.command_not_allowed("test"),
            ErrorCatalog.file_not_found("test.txt"),
            ErrorCatalog.yaml_parse_error("test.yaml", ValueError("error")),
            ErrorCatalog.missing_required_field("field"),
            ErrorCatalog.command_failed("cmd", 1, "error"),
            ErrorCatalog.budget_exceeded(10.0, 5.0),
            ErrorCatalog.human_approval_required("hash", "id"),
            ErrorCatalog.compression_failed(RuntimeError("error")),
        ]

        for error in errors:
            formatted = error.format()
            assert all(ord(c) < 128 or c in ["\n"] for c in formatted)


class TestErrorIntegration:
    """Integration tests for realistic scenarios"""

    def test_complete_error_workflow(self):
        """Test complete error workflow from creation to display"""
        # Create error
        error = ErrorCatalog.command_not_allowed("rm")

        # Format for display
        formatted = error.format(include_details=True)

        # Should contain all expected sections
        assert "[ERROR]" in formatted
        assert "[SUGGESTION]" in formatted
        assert "[DETAILS]" in formatted

        # Should be actionable
        assert "ALLOWED_CMDS" in formatted
        assert "task_executor.py" in formatted

    def test_error_without_suggestion_still_helpful(self):
        """Test that errors without suggestions are still clear"""
        error = EnhancedError(
            message="Unexpected error occurred",
            severity=ErrorSeverity.ERROR,
            details={"trace_id": "abc123"},
        )

        formatted = error.format()

        # Should still provide useful information
        assert "[ERROR]" in formatted
        assert "[DETAILS]" in formatted
        assert "abc123" in formatted
