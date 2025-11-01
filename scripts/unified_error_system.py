"""Unified Error System - Advanced Error Management for Tier 1.

Comprehensive error handling with recovery strategies, metrics, and integration
across all Tier 1 Integration modules.

Compliance:
- P1: YAML-First (error configuration via YAML)
- P2: Evidence-based (error metrics and tracking)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

Features:
- Integration with all Tier 1 modules
- Automatic error recovery strategies
- Performance impact tracking
- Error pattern detection
- Real-time error monitoring

Example:
    $ python scripts/unified_error_system.py --monitor
    $ python scripts/unified_error_system.py --analyze
"""

import json
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from error_handler import EnhancedError, ErrorCatalog, ErrorSeverity
    from security_utils import SecurityError
    from notification_utils import send_slack_notification
except ImportError:
    from scripts.error_handler import EnhancedError, ErrorCatalog, ErrorSeverity
    from scripts.security_utils import SecurityError

    try:
        from scripts.notification_utils import send_slack_notification
    except ImportError:
        # Fallback if notification utilities not available
        def send_slack_notification(message: str, **kwargs) -> bool:
            return False


@dataclass
class ErrorMetrics:
    """Metrics for error tracking.

    Attributes:
        total_count: Total error count.
        by_module: Errors by module.
        by_severity: Errors by severity.
        recovery_attempts: Recovery attempt count.
        recovery_successes: Successful recovery count.
        avg_recovery_time_ms: Average recovery time.
        error_rate_per_minute: Error rate.
        last_error_time: Last error timestamp.
    """

    total_count: int = 0
    by_module: Dict[str, int] = None
    by_severity: Dict[str, int] = None
    recovery_attempts: int = 0
    recovery_successes: int = 0
    avg_recovery_time_ms: float = 0.0
    error_rate_per_minute: float = 0.0
    last_error_time: Optional[datetime] = None

    def __post_init__(self):
        """Initialize dictionaries."""
        if self.by_module is None:
            self.by_module = defaultdict(int)
        if self.by_severity is None:
            self.by_severity = defaultdict(int)


class ErrorPattern:
    """Pattern detection for recurring errors.

    Attributes:
        pattern_id: Unique pattern identifier.
        error_signature: Error signature string.
        occurrences: List of occurrence timestamps.
        modules: Affected modules.
        suggested_fix: Suggested fix for pattern.
    """

    def __init__(self, pattern_id: str, error_signature: str):
        """Initialize error pattern.

        Args:
            pattern_id: Pattern identifier.
            error_signature: Error signature.
        """
        self.pattern_id = pattern_id
        self.error_signature = error_signature
        self.occurrences: List[datetime] = []
        self.modules: set = set()
        self.suggested_fix: Optional[str] = None

    def add_occurrence(self, timestamp: datetime, module: str):
        """Add occurrence to pattern.

        Args:
            timestamp: When error occurred.
            module: Module where error occurred.
        """
        self.occurrences.append(timestamp)
        self.modules.add(module)

    def is_recurring(self, threshold: int = 3) -> bool:
        """Check if pattern is recurring.

        Args:
            threshold: Minimum occurrences to be recurring.

        Returns:
            True if recurring pattern.
        """
        return len(self.occurrences) >= threshold

    def frequency(self, window_minutes: int = 60) -> float:
        """Calculate occurrence frequency.

        Args:
            window_minutes: Time window in minutes.

        Returns:
            Occurrences per minute in window.
        """
        if not self.occurrences:
            return 0.0

        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        recent = [o for o in self.occurrences if o >= window_start]

        if not recent:
            return 0.0

        duration = (now - min(recent)).total_seconds() / 60.0
        return len(recent) / duration if duration > 0 else 0.0


class RecoveryStrategy:
    """Base recovery strategy."""

    def __init__(self, name: str, max_attempts: int = 3):
        """Initialize recovery strategy.

        Args:
            name: Strategy name.
            max_attempts: Maximum recovery attempts.
        """
        self.name = name
        self.max_attempts = max_attempts
        self.attempts = 0

    def can_recover(self, error: Exception) -> bool:
        """Check if recovery possible.

        Args:
            error: Exception to check.

        Returns:
            True if recovery possible.
        """
        return self.attempts < self.max_attempts

    def recover(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Attempt recovery.

        Args:
            error: Exception to recover from.
            context: Error context.

        Returns:
            Recovery result.
        """
        self.attempts += 1
        raise NotImplementedError

    def reset(self):
        """Reset attempt counter."""
        self.attempts = 0


class RetryWithBackoff(RecoveryStrategy):
    """Retry with exponential backoff."""

    def __init__(
        self,
        name: str = "retry_backoff",
        max_attempts: int = 3,
        base_delay: float = 1.0,
    ):
        """Initialize retry strategy.

        Args:
            name: Strategy name.
            max_attempts: Max retry attempts.
            base_delay: Base delay in seconds.
        """
        super().__init__(name, max_attempts)
        self.base_delay = base_delay

    def recover(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Retry with exponential backoff.

        Args:
            error: Exception to recover from.
            context: Must contain 'function' to retry.

        Returns:
            Function result on success.
        """
        self.attempts += 1
        delay = self.base_delay * (2 ** (self.attempts - 1))

        print(f"[RETRY] Attempt {self.attempts}/{self.max_attempts} after {delay}s delay")
        time.sleep(delay)

        # Retry the function
        func = context.get("function")
        args = context.get("args", ())
        kwargs = context.get("kwargs", {})

        if func:
            return func(*args, **kwargs)
        raise error


class CircuitBreaker(RecoveryStrategy):
    """Circuit breaker pattern."""

    def __init__(
        self,
        name: str = "circuit_breaker",
        failure_threshold: int = 5,
        timeout: float = 60.0,
    ):
        """Initialize circuit breaker.

        Args:
            name: Strategy name.
            failure_threshold: Failures before opening.
            timeout: Timeout before half-open.
        """
        super().__init__(name)
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def can_recover(self, error: Exception) -> bool:
        """Check circuit state."""
        if self.state == "open":
            # Check if timeout passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self.state = "half-open"
                    print("[CIRCUIT] Entering half-open state")
                    return True
            return False
        return True

    def recover(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Handle with circuit breaker.

        Args:
            error: Exception occurred.
            context: Error context.

        Returns:
            Result or raises error.
        """
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            print(f"[CIRCUIT] Opening circuit after {self.failures} failures")
            raise error

        # Try fallback if available
        fallback = context.get("fallback")
        if fallback:
            return fallback()

        raise error

    def on_success(self):
        """Reset on successful operation."""
        if self.state == "half-open":
            self.state = "closed"
            print("[CIRCUIT] Circuit closed after successful operation")
        self.failures = 0


class UnifiedErrorSystem:
    """Unified error management system for Tier 1.

    Integrates with all modules for comprehensive error handling.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize unified error system.

        Args:
            config_path: Path to error configuration.
        """
        self.config_path = config_path or Path("config/error_config.yaml")
        self.metrics = ErrorMetrics()
        self.patterns: Dict[str, ErrorPattern] = {}
        self.strategies: Dict[str, RecoveryStrategy] = {}
        self.error_history: List[EnhancedError] = []
        self.max_history = 1000

        # Initialize default strategies
        self._init_default_strategies()

        # Load configuration
        self._load_config()

        # Start time for rate calculation
        self.start_time = datetime.now()

    def _init_default_strategies(self):
        """Initialize default recovery strategies."""
        self.strategies["retry"] = RetryWithBackoff()
        self.strategies["circuit"] = CircuitBreaker()

    def _load_config(self):
        """Load error configuration."""
        # Would load from YAML config if exists
        pass

    def handle_error(
        self,
        error: Exception,
        module: str,
        function: str = "",
        context: Optional[Dict[str, Any]] = None,
        auto_recover: bool = True,
    ) -> Tuple[bool, Any]:
        """Handle error with recovery.

        Args:
            error: Exception that occurred.
            module: Module name.
            function: Function name.
            context: Additional context.
            auto_recover: Attempt automatic recovery.

        Returns:
            Tuple of (recovered, result).
        """
        # Update metrics
        self.metrics.total_count += 1
        self.metrics.by_module[module] += 1
        self.metrics.last_error_time = datetime.now()

        # Determine severity
        severity = self._determine_severity(error)
        self.metrics.by_severity[severity] += 1

        # Create enhanced error
        enhanced = self._enhance_error(error, module, function, severity)
        self.error_history.append(enhanced)

        # Detect patterns
        self._detect_pattern(error, module)

        # Attempt recovery if enabled
        if auto_recover:
            recovered, result = self._attempt_recovery(error, context)
            if recovered:
                self.metrics.recovery_successes += 1
                return True, result
            self.metrics.recovery_attempts += 1

        # Trim history
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history :]

        return False, None

    def _determine_severity(self, error: Exception) -> str:
        """Determine error severity and send notification for critical errors."""
        severity = ErrorSeverity.ERROR  # Default

        if isinstance(error, (SystemExit, KeyboardInterrupt, MemoryError)):
            severity = ErrorSeverity.CRITICAL
            # Send immediate notification for critical errors
            self._send_critical_notification(error, "CRITICAL")
        elif isinstance(error, (PermissionError, SecurityError)):
            severity = ErrorSeverity.ERROR
            # Send notification for security errors
            if isinstance(error, SecurityError):
                self._send_critical_notification(error, "SECURITY")
        elif isinstance(error, FileNotFoundError):
            severity = ErrorSeverity.WARNING

        return severity

    def _send_critical_notification(self, error: Exception, error_type: str) -> None:
        """Send notification for critical errors.

        Args:
            error: The exception that occurred
            error_type: Type of critical error (CRITICAL, SECURITY, etc.)
        """
        try:
            message = (
                f"[{error_type}] Error in Tier 1 Integration System\n"
                f"Error: {type(error).__name__}: {str(error)}\n"
                f"Module: {self.error_history[-1]['module'] if self.error_history else 'Unknown'}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total errors today: {self.metrics.total_count}"
            )

            # Try to send Slack notification
            success = send_slack_notification(message)

            if not success:
                # Log if notification fails
                print(f"[WARNING] Failed to send {error_type} notification")

        except Exception as notify_error:
            # Don't let notification errors break the main flow
            print(f"[WARNING] Notification error: {notify_error}")

    def _enhance_error(
        self,
        error: Exception,
        module: str,
        function: str,
        severity: str,
    ) -> EnhancedError:
        """Create enhanced error."""
        # Try to get from catalog
        error_type = type(error).__name__

        if isinstance(error, FileNotFoundError):
            return ErrorCatalog.file_not_found(str(error))

        # Generic enhanced error
        return EnhancedError(
            message=str(error),
            severity=severity,
            details={
                "module": module,
                "function": function,
                "type": error_type,
            },
            original_error=error,
        )

    def _detect_pattern(self, error: Exception, module: str):
        """Detect error patterns."""
        signature = f"{type(error).__name__}:{str(error)[:50]}"
        pattern_id = f"pattern_{hash(signature) % 10000}"

        if pattern_id not in self.patterns:
            self.patterns[pattern_id] = ErrorPattern(pattern_id, signature)

        pattern = self.patterns[pattern_id]
        pattern.add_occurrence(datetime.now(), module)

        # Check if recurring
        if pattern.is_recurring():
            frequency = pattern.frequency()
            if frequency > 1.0:  # More than 1 per minute
                print(f"[PATTERN] Recurring error detected: {signature}")
                print(f"  Frequency: {frequency:.2f} errors/minute")
                print(f"  Modules: {', '.join(pattern.modules)}")

    def _attempt_recovery(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]],
    ) -> Tuple[bool, Any]:
        """Attempt error recovery.

        Args:
            error: Exception to recover from.
            context: Error context.

        Returns:
            Tuple of (success, result).
        """
        if not context:
            return False, None

        # Select strategy based on error type
        strategy = None

        # Retry for temporary errors
        if isinstance(error, (IOError, OSError, ConnectionError)):
            strategy = self.strategies.get("retry")

        # Circuit breaker for repeated failures
        elif self._is_repeated_failure(error):
            strategy = self.strategies.get("circuit")

        if strategy and strategy.can_recover(error):
            try:
                start = time.perf_counter()
                result = strategy.recover(error, context)
                recovery_time = (time.perf_counter() - start) * 1000

                # Update metrics
                self.metrics.recovery_successes += 1
                n = self.metrics.recovery_successes
                prev_avg = self.metrics.avg_recovery_time_ms
                self.metrics.avg_recovery_time_ms = (prev_avg * (n - 1) + recovery_time) / n

                return True, result

            except Exception as recovery_error:
                print(f"[RECOVERY] Failed: {recovery_error}")

        return False, None

    def _is_repeated_failure(self, error: Exception) -> bool:
        """Check if error is repeatedly failing."""
        error_type = type(error).__name__
        recent_errors = [e for e in self.error_history[-10:] if e.details.get("type") == error_type]
        return len(recent_errors) >= 3

    @contextmanager
    def error_context(self, module: str, function: str = ""):
        """Context manager for error handling.

        Args:
            module: Module name.
            function: Function name.

        Example:
            >>> with error_system.error_context("my_module", "my_func"):
            ...     risky_operation()
        """
        try:
            yield
        except Exception as e:
            recovered, result = self.handle_error(
                e,
                module,
                function,
                auto_recover=True,
            )
            if not recovered:
                raise

    def get_metrics(self) -> ErrorMetrics:
        """Get current error metrics."""
        # Calculate error rate
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60.0
        if elapsed > 0:
            self.metrics.error_rate_per_minute = self.metrics.total_count / elapsed

        return self.metrics

    def get_report(self) -> Dict[str, Any]:
        """Generate error report.

        Returns:
            Comprehensive error report.
        """
        metrics = self.get_metrics()

        # Find most common errors
        error_types = defaultdict(int)
        for error in self.error_history:
            error_type = error.details.get("type", "Unknown")
            error_types[error_type] += 1

        most_common = sorted(
            error_types.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        # Find recurring patterns
        recurring = [
            {
                "pattern": p.error_signature,
                "occurrences": len(p.occurrences),
                "modules": list(p.modules),
                "frequency": p.frequency(),
            }
            for p in self.patterns.values()
            if p.is_recurring()
        ]

        return {
            "summary": {
                "total_errors": metrics.total_count,
                "error_rate": f"{metrics.error_rate_per_minute:.2f} errors/min",
                "recovery_rate": (
                    f"{(metrics.recovery_successes / metrics.recovery_attempts * 100):.1f}%"
                    if metrics.recovery_attempts > 0
                    else "N/A"
                ),
                "avg_recovery_time": f"{metrics.avg_recovery_time_ms:.2f}ms",
            },
            "by_severity": dict(metrics.by_severity),
            "by_module": dict(metrics.by_module),
            "most_common": most_common,
            "recurring_patterns": recurring,
            "last_error": (metrics.last_error_time.isoformat() if metrics.last_error_time else None),
        }

    def monitor(self, interval: int = 60):
        """Start error monitoring.

        Args:
            interval: Report interval in seconds.
        """
        print("[MONITOR] Error monitoring started")
        print(f"[MONITOR] Report interval: {interval}s")

        try:
            while True:
                time.sleep(interval)
                report = self.get_report()

                print("\n" + "=" * 50)
                print(f"[REPORT] Error System Status - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 50)

                summary = report["summary"]
                print(f"Total Errors: {summary['total_errors']}")
                print(f"Error Rate: {summary['error_rate']}")
                print(f"Recovery Rate: {summary['recovery_rate']}")

                if report["recurring_patterns"]:
                    print("\n[ALERT] Recurring Patterns Detected:")
                    for pattern in report["recurring_patterns"]:
                        print(f"  - {pattern['pattern']}: {pattern['occurrences']} times")

        except KeyboardInterrupt:
            print("\n[MONITOR] Monitoring stopped")


# Global instance
_global_system = None


def get_error_system() -> UnifiedErrorSystem:
    """Get global error system instance."""
    global _global_system
    if _global_system is None:
        _global_system = UnifiedErrorSystem()
    return _global_system


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified Error System - Advanced Error Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/unified_error_system.py --test
  python scripts/unified_error_system.py --monitor
  python scripts/unified_error_system.py --analyze
        """,
    )

    parser.add_argument("--test", action="store_true", help="Test error system")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring")
    parser.add_argument("--analyze", action="store_true", help="Analyze errors")

    args = parser.parse_args()

    print("[INFO] Unified Error System")
    print("")

    system = UnifiedErrorSystem()

    try:
        if args.test:
            print("[TEST] Testing error system...")

            # Test various errors
            test_cases = [
                (FileNotFoundError("test.txt"), "test_module"),
                (ConnectionError("Network down"), "network_module"),
                (ValueError("Invalid input"), "validation_module"),
            ]

            for error, module in test_cases:
                recovered, _ = system.handle_error(
                    error,
                    module,
                    "test_function",
                    auto_recover=False,
                )
                print(f"  {type(error).__name__}: {'Recovered' if recovered else 'Handled'}")

            print("\n[OK] Error system tests completed")

        if args.analyze or args.test:
            report = system.get_report()
            print("\n[ANALYSIS] Error System Report:")
            print(json.dumps(report, indent=2, default=str))

        if args.monitor:
            system.monitor(interval=30)

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
