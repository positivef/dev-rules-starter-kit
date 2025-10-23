#!/usr/bin/env python3
"""
Enhanced Error Handler for TaskExecutor

Purpose:
- User-friendly error messages with actionable suggestions
- Error categorization and severity levels
- Context-aware error formatting

Constitutional Compliance:
- [P6] Observability
- [P10] Windows UTF-8 (ASCII-only output)
"""

from typing import Optional, Dict
from pathlib import Path
import traceback


class ErrorSeverity:
    """Error severity levels"""

    CRITICAL = "CRITICAL"  # System cannot continue
    ERROR = "ERROR"  # Operation failed, but recoverable
    WARNING = "WARNING"  # Potential issue, operation continues
    INFO = "INFO"  # Informational message


class EnhancedError:
    """Enhanced error with user-friendly messaging"""

    def __init__(
        self,
        message: str,
        severity: str = ErrorSeverity.ERROR,
        suggestion: Optional[str] = None,
        details: Optional[Dict] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize enhanced error.

        Args:
            message: User-friendly error message
            severity: Error severity level
            suggestion: Actionable suggestion to fix the error
            details: Additional context details
            original_error: Original exception if available
        """
        self.message = message
        self.severity = severity
        self.suggestion = suggestion
        self.details = details or {}
        self.original_error = original_error

    def format(self, include_details: bool = True, include_traceback: bool = False) -> str:
        """
        Format error for display.

        Args:
            include_details: Whether to include technical details
            include_traceback: Whether to include full traceback

        Returns:
            Formatted error string
        """
        lines = []

        # Header with severity
        lines.append(f"[{self.severity}] {self.message}")

        # Suggestion (if available)
        if self.suggestion:
            lines.append(f"\n[SUGGESTION] {self.suggestion}")

        # Details (if enabled)
        if include_details and self.details:
            lines.append("\n[DETAILS]")
            for key, value in self.details.items():
                lines.append(f"   {key}: {value}")

        # Traceback (if enabled and available)
        if include_traceback and self.original_error:
            lines.append("\n[TRACEBACK]")
            tb_lines = traceback.format_exception(
                type(self.original_error), self.original_error, self.original_error.__traceback__
            )
            for line in tb_lines:
                lines.append(f"   {line.rstrip()}")

        return "\n".join(lines)


class ErrorCatalog:
    """Catalog of common errors with helpful messages"""

    @staticmethod
    def command_not_allowed(cmd: str) -> EnhancedError:
        """Command not in allowlist"""
        return EnhancedError(
            message=f"Command '{cmd}' is not in the allowed commands list",
            severity=ErrorSeverity.ERROR,
            suggestion=(
                f"Add '{cmd}' to ALLOWED_CMDS in scripts/task_executor.py if this is a safe command.\n"
                "   Security check: Ensure the command doesn't pose security risks."
            ),
            details={"command": cmd, "file": "scripts/task_executor.py", "variable": "ALLOWED_CMDS"},
        )

    @staticmethod
    def file_not_found(filepath: str) -> EnhancedError:
        """File not found"""
        path = Path(filepath)
        return EnhancedError(
            message=f"File not found: {filepath}",
            severity=ErrorSeverity.ERROR,
            suggestion=(
                f"Check if the file exists:\n"
                f"   - Expected path: {path.absolute()}\n"
                f"   - Parent directory exists: {path.parent.exists()}\n"
                "   - Check for typos in the file path"
            ),
            details={"filepath": filepath, "absolute_path": str(path.absolute()), "exists": path.exists()},
        )

    @staticmethod
    def yaml_parse_error(filepath: str, error: Exception) -> EnhancedError:
        """YAML parsing error"""
        return EnhancedError(
            message=f"Failed to parse YAML file: {filepath}",
            severity=ErrorSeverity.ERROR,
            suggestion=(
                "Check YAML syntax:\n"
                "   - Proper indentation (use spaces, not tabs)\n"
                "   - Matching quotes and brackets\n"
                "   - Valid YAML syntax (https://yaml.org/spec/1.2/spec.html)"
            ),
            details={"filepath": filepath, "error_type": type(error).__name__, "error_message": str(error)},
            original_error=error,
        )

    @staticmethod
    def missing_required_field(field: str, context: str = "") -> EnhancedError:
        """Required field missing in YAML"""
        return EnhancedError(
            message=f"Required field '{field}' is missing{' in ' + context if context else ''}",
            severity=ErrorSeverity.ERROR,
            suggestion=(
                f"Add the required field to your YAML file:\n"
                f"   {field}: <value>\n"
                "   Check TASKS/TEMPLATE.yaml for examples"
            ),
            details={"field": field, "context": context, "template": "TASKS/TEMPLATE.yaml"},
        )

    @staticmethod
    def command_failed(cmd: str, return_code: int, stderr: str) -> EnhancedError:
        """Command execution failed"""
        # Extract meaningful error from stderr
        stderr_preview = stderr[:200] + "..." if len(stderr) > 200 else stderr

        return EnhancedError(
            message=f"Command failed with exit code {return_code}: {cmd}",
            severity=ErrorSeverity.ERROR,
            suggestion=(
                "Troubleshooting steps:\n"
                "   1. Check if all required dependencies are installed\n"
                "   2. Verify the command arguments are correct\n"
                "   3. Check if input files exist\n"
                "   4. Review the error message in [DETAILS] section"
            ),
            details={"command": cmd, "exit_code": return_code, "stderr_preview": stderr_preview},
        )

    @staticmethod
    def budget_exceeded(estimated: float, budget: float) -> EnhancedError:
        """Budget exceeded"""
        return EnhancedError(
            message=f"Estimated cost ${estimated:.2f} exceeds budget ${budget:.2f}",
            severity=ErrorSeverity.ERROR,
            suggestion=(
                "Options to proceed:\n"
                f"   1. Increase budget in YAML: cost_budget_usd: {estimated * 1.2:.2f}\n"
                "   2. Reduce task scope to lower costs\n"
                "   3. Set cost_hard_limit: false to allow exceeding budget"
            ),
            details={"estimated_cost": estimated, "budget": budget, "overage": estimated - budget},
        )

    @staticmethod
    def human_approval_required(hash_value: str, task_id: str) -> EnhancedError:
        """Human approval required"""
        return EnhancedError(
            message="Human approval is required before execution",
            severity=ErrorSeverity.WARNING,
            suggestion=(
                f"Review the execution plan and approve:\n"
                f"   1. Run with --plan flag to review: python scripts/task_executor.py TASKS/{{task}}.yaml --plan\n"
                f"   2. Approve: echo '{hash_value}' > RUNS/{task_id}/.human_approved\n"
                f"   3. Execute: python scripts/task_executor.py TASKS/{{task}}.yaml"
            ),
            details={"task_id": task_id, "approval_hash": hash_value},
        )

    @staticmethod
    def compression_failed(error: Exception) -> EnhancedError:
        """Prompt compression failed"""
        return EnhancedError(
            message="Prompt compression failed, continuing with uncompressed prompts",
            severity=ErrorSeverity.WARNING,
            suggestion=(
                "This is a non-critical warning. The task will continue with original prompts.\n" "   No action needed."
            ),
            details={"error_type": type(error).__name__, "error_message": str(error)},
            original_error=error,
        )


def format_error_for_user(error: Exception, context: Optional[str] = None) -> str:
    """
    Format any exception for user-friendly display.

    Args:
        error: The exception to format
        context: Optional context about where the error occurred

    Returns:
        Formatted error string
    """
    error_type = type(error).__name__
    error_msg = str(error)

    lines = [f"[ERROR] {error_type}: {error_msg}"]

    if context:
        lines.append(f"\n[CONTEXT] {context}")

    lines.append("\n[HELP] For more details, run with verbose mode or check the logs")

    return "\n".join(lines)
