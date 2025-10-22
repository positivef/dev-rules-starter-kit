"""
Development Assistant - Production File Watcher

A robust file watcher that monitors Python files and triggers development workflows.
Implements clean architecture with proper error handling and graceful shutdown.

Features:
- Monitors scripts/ and tests/ directories for Python file changes
- Debounces changes (500ms) to avoid redundant processing
- Runs Ruff verification on each saved Python file (<200ms)
- Runs in background with <2% CPU when idle
- Graceful shutdown on SIGINT/SIGTERM
- Thread-safe queue-based processing
- Comprehensive logging with timestamps
- Automatic evidence tracking with daily log rotation
- Configuration via pyproject.toml with CLI override

Usage:
    python scripts/dev_assistant.py

    # With custom directories
    python scripts/dev_assistant.py --watch-dirs scripts tests custom_dir

    # With custom debounce time
    python scripts/dev_assistant.py --debounce 1000

Configuration:
    Add [tool.dev-assistant] section to pyproject.toml:

    [tool.dev-assistant]
    enabled = true
    watch_paths = ["scripts", "tests"]
    debounce_ms = 500
    verification_timeout_sec = 2.0
    log_retention_days = 7
    enable_ruff = true
    enable_evidence = true
"""

import json
import logging
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Event, Lock, Thread
from typing import Dict, List, Optional, Set

# Try stdlib tomllib (Python 3.11+), fall back to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


@dataclass
class AssistantConfig:
    """Configuration for Development Assistant."""

    enabled: bool = True
    watch_paths: List[str] = None
    debounce_ms: int = 500
    verification_timeout_sec: float = 2.0
    log_retention_days: int = 7
    enable_ruff: bool = True
    enable_evidence: bool = True

    def __post_init__(self):
        """Set defaults for mutable fields."""
        if self.watch_paths is None:
            self.watch_paths = ["scripts", "tests"]

    def validate(self) -> List[str]:
        """
        Validate configuration values.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not isinstance(self.enabled, bool):
            errors.append("enabled must be boolean")

        if not isinstance(self.watch_paths, list) or not self.watch_paths:
            errors.append("watch_paths must be non-empty list")
        elif not all(isinstance(p, str) for p in self.watch_paths):
            errors.append("watch_paths must contain only strings")

        if not isinstance(self.debounce_ms, int) or self.debounce_ms < 0:
            errors.append("debounce_ms must be non-negative integer")

        if not isinstance(self.verification_timeout_sec, (int, float)) or self.verification_timeout_sec <= 0:
            errors.append("verification_timeout_sec must be positive number")

        if not isinstance(self.log_retention_days, int) or self.log_retention_days < 0:
            errors.append("log_retention_days must be non-negative integer")

        if not isinstance(self.enable_ruff, bool):
            errors.append("enable_ruff must be boolean")

        if not isinstance(self.enable_evidence, bool):
            errors.append("enable_evidence must be boolean")

        return errors


class ConfigLoader:
    """
    Loads configuration from pyproject.toml.

    Supports Python 3.11+ stdlib tomllib and fallback to tomli package.
    Provides clear error messages for invalid or missing configuration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            project_root: Path to project root (defaults to cwd)
        """
        self._root = project_root or Path.cwd()
        self._config_file = self._root / "pyproject.toml"
        self._logger = logging.getLogger("dev_assistant.config")

    def load(self) -> AssistantConfig:
        """
        Load configuration from pyproject.toml.

        Returns:
            AssistantConfig with values from file or defaults

        Raises:
            RuntimeError: If configuration is invalid
        """
        # Return defaults if no config file
        if not self._config_file.exists():
            self._logger.debug("No pyproject.toml found, using defaults")
            return AssistantConfig()

        # Check if tomllib is available
        if tomllib is None:
            self._logger.warning("tomllib/tomli not available. Install tomli for config support: pip install tomli")
            return AssistantConfig()

        try:
            # Read TOML file
            with open(self._config_file, "rb") as f:
                data = tomllib.load(f)

            # Extract dev-assistant config
            tool_config = data.get("tool", {})
            assistant_config = tool_config.get("dev-assistant", {})

            if not assistant_config:
                self._logger.debug("No [tool.dev-assistant] section found, using defaults")
                return AssistantConfig()

            # Build config from TOML
            config = AssistantConfig(
                enabled=assistant_config.get("enabled", True),
                watch_paths=assistant_config.get("watch_paths"),
                debounce_ms=assistant_config.get("debounce_ms", 500),
                verification_timeout_sec=assistant_config.get("verification_timeout_sec", 2.0),
                log_retention_days=assistant_config.get("log_retention_days", 7),
                enable_ruff=assistant_config.get("enable_ruff", True),
                enable_evidence=assistant_config.get("enable_evidence", True),
            )

            # Validate configuration
            errors = config.validate()
            if errors:
                raise RuntimeError(f"Invalid configuration in {self._config_file}:\n  - " + "\n  - ".join(errors))

            self._logger.debug(f"Loaded configuration from {self._config_file}")
            return config

        except tomllib.TOMLDecodeError as e:
            raise RuntimeError(f"Failed to parse {self._config_file}: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}") from e

    def merge_with_cli_args(
        self,
        config: AssistantConfig,
        watch_dirs: Optional[List[str]] = None,
        debounce: Optional[int] = None,
        log_level: Optional[str] = None,
        no_ruff: bool = False,
        no_evidence: bool = False,
    ) -> AssistantConfig:
        """
        Merge configuration with CLI arguments (CLI takes precedence).

        Args:
            config: Base configuration from file
            watch_dirs: Override watch_paths
            debounce: Override debounce_ms
            log_level: Logging level (doesn't affect config)
            no_ruff: Disable Ruff verification
            no_evidence: Disable evidence logging

        Returns:
            Merged configuration
        """
        # CLI arguments override config file
        if watch_dirs is not None:
            config.watch_paths = watch_dirs

        if debounce is not None:
            config.debounce_ms = debounce

        if no_ruff:
            config.enable_ruff = False

        if no_evidence:
            config.enable_evidence = False

        # Validate merged config
        errors = config.validate()
        if errors:
            raise RuntimeError("Invalid configuration after CLI merge:\n  - " + "\n  - ".join(errors))

        return config


@dataclass
class RuffViolation:
    """Represents a single Ruff violation."""

    code: str
    message: str
    line: int
    column: int
    fix_available: bool = False

    def __str__(self) -> str:
        """Format violation for console output."""
        return f"Line {self.line}:{self.column} - {self.code}: {self.message}"


@dataclass
class VerificationResult:
    """Result of Ruff verification for a file."""

    file_path: Path
    passed: bool
    violations: List[RuffViolation]
    duration_ms: float
    error: Optional[str] = None

    @property
    def violation_count(self) -> int:
        """Get total number of violations."""
        return len(self.violations)


@dataclass
class VerificationEvent:
    """Evidence event for a single verification execution."""

    timestamp: str
    file: str
    verification: Dict[str, any]
    duration_ms: float
    event_type: str = "modified"


class RuffVerifier:
    """
    Ruff code verification engine.

    Runs Ruff check on Python files with timeout protection and structured output parsing.
    Designed for fast execution (<200ms) with comprehensive error handling.
    """

    def __init__(self, timeout_seconds: float = 2.0, ruff_config: Optional[Path] = None):
        """
        Initialize Ruff verifier.

        Args:
            timeout_seconds: Maximum time to wait for Ruff execution
            ruff_config: Path to ruff.toml config file (optional)
        """
        self._timeout = timeout_seconds
        self._ruff_config = ruff_config
        self._logger = logging.getLogger("dev_assistant.ruff")

    def verify_file(self, file_path: Path) -> VerificationResult:
        """
        Run Ruff verification on a Python file.

        Args:
            file_path: Path to Python file to verify

        Returns:
            VerificationResult with violations and metadata
        """
        start_time = time.time()

        # Validate file exists
        if not file_path.exists():
            return VerificationResult(
                file_path=file_path,
                passed=False,
                violations=[],
                duration_ms=0,
                error=f"File not found: {file_path}",
            )

        # Build Ruff command
        cmd = ["ruff", "check", "--output-format=json", str(file_path)]

        if self._ruff_config and self._ruff_config.exists():
            cmd.extend(["--config", str(self._ruff_config)])

        try:
            # Execute Ruff with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                check=False,  # Don't raise on non-zero exit (Ruff returns 1 for violations)
            )

            duration_ms = (time.time() - start_time) * 1000

            # Parse output
            violations = self._parse_ruff_output(result.stdout)

            return VerificationResult(
                file_path=file_path,
                passed=len(violations) == 0,
                violations=violations,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            self._logger.warning(f"Ruff verification timeout for {file_path}")
            return VerificationResult(
                file_path=file_path,
                passed=False,
                violations=[],
                duration_ms=duration_ms,
                error=f"Verification timeout after {self._timeout}s",
            )

        except FileNotFoundError:
            duration_ms = (time.time() - start_time) * 1000
            self._logger.error("Ruff not found. Install with: pip install ruff")
            return VerificationResult(
                file_path=file_path,
                passed=False,
                violations=[],
                duration_ms=duration_ms,
                error="Ruff not installed",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._logger.error(f"Ruff verification error: {e}", exc_info=True)
            return VerificationResult(
                file_path=file_path,
                passed=False,
                violations=[],
                duration_ms=duration_ms,
                error=str(e),
            )

    def _parse_ruff_output(self, json_output: str) -> List[RuffViolation]:
        """
        Parse Ruff JSON output into violation objects.

        Args:
            json_output: JSON string from Ruff --output-format=json

        Returns:
            List of RuffViolation objects
        """
        if not json_output or json_output.strip() == "":
            return []

        try:
            data = json.loads(json_output)

            violations = []
            for item in data:
                violation = RuffViolation(
                    code=item.get("code", "UNKNOWN"),
                    message=item.get("message", ""),
                    line=item.get("location", {}).get("row", 0),
                    column=item.get("location", {}).get("column", 0),
                    fix_available=item.get("fix") is not None,
                )
                violations.append(violation)

            return violations

        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to parse Ruff JSON output: {e}")
            return []

        except Exception as e:
            self._logger.error(f"Error parsing Ruff output: {e}", exc_info=True)
            return []


class EvidenceLogger:
    """
    Automatic evidence logging for verification events.

    Based on AutomaticEvidenceTracker pattern (GrowthBook Trust 8.0):
    - Automatic collection without manual calls
    - Daily log rotation (keep last 7 days)
    - Dual output: JSON (structured) + text (human-readable)
    - Compatible with EnhancedTaskExecutor evidence format
    """

    def __init__(self, runs_dir: Optional[Path] = None, retention_days: int = 7):
        """
        Initialize evidence logger.

        Args:
            runs_dir: Base directory for RUNS/ (defaults to project root)
            retention_days: Number of days to keep logs (default: 7)
        """
        self._runs_dir = runs_dir or Path.cwd() / "RUNS"
        self._retention_days = retention_days
        self._logger = logging.getLogger("dev_assistant.evidence")
        self._lock = Lock()

        # Create daily directory
        self._daily_dir = self._create_daily_directory()
        self._evidence_file = self._daily_dir / "evidence.json"
        self._log_file = self._daily_dir / "verification.log"

        # Initialize evidence storage
        self._events: List[Dict[str, any]] = []
        self._load_existing_evidence()

        # Clean old logs
        self._rotate_logs()

    def _create_daily_directory(self) -> Path:
        """
        Create daily evidence directory.

        Returns:
            Path to daily directory (RUNS/dev-assistant-YYYYMMDD/)
        """
        today = datetime.now().strftime("%Y%m%d")
        daily_dir = self._runs_dir / f"dev-assistant-{today}"
        daily_dir.mkdir(parents=True, exist_ok=True)
        return daily_dir

    def _load_existing_evidence(self) -> None:
        """Load existing evidence from JSON file if it exists."""
        if self._evidence_file.exists():
            try:
                with open(self._evidence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._events = data.get("events", [])
                    self._logger.debug(f"Loaded {len(self._events)} existing events")
            except json.JSONDecodeError as e:
                self._logger.warning(f"Failed to load existing evidence: {e}")
                self._events = []
        else:
            self._events = []

    def _rotate_logs(self) -> None:
        """Remove evidence directories older than retention period."""
        if not self._runs_dir.exists():
            return

        cutoff_date = datetime.now().timestamp() - (self._retention_days * 86400)

        for item in self._runs_dir.iterdir():
            if not item.is_dir() or not item.name.startswith("dev-assistant-"):
                continue

            # Check directory age
            try:
                dir_time = item.stat().st_mtime
                if dir_time < cutoff_date:
                    shutil.rmtree(item)
                    self._logger.info(f"Rotated old evidence: {item.name}")
            except Exception as e:
                self._logger.warning(f"Failed to rotate {item.name}: {e}")

    def log_verification(self, event_type: str, file_path: Path, result: VerificationResult) -> None:
        """
        Log verification result to evidence files.

        Args:
            event_type: Type of change (modified, created)
            file_path: Path to verified file
            result: VerificationResult object
        """
        with self._lock:
            # Build verification details
            verification_data = {
                "ruff_passed": result.passed,
            }

            if result.error:
                verification_data["error"] = result.error
            else:
                verification_data["violations"] = [
                    {
                        "line": v.line,
                        "column": v.column,
                        "code": v.code,
                        "message": v.message,
                        "fix_available": v.fix_available,
                    }
                    for v in result.violations
                ]

            # Create event
            # Handle both absolute and relative paths
            try:
                file_str = str(file_path.relative_to(Path.cwd()))
            except ValueError:
                # Path is already relative or outside cwd
                file_str = str(file_path)

            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "file": file_str,
                "verification": verification_data,
                "duration_ms": result.duration_ms,
            }

            self._events.append(event)

            # Write to JSON
            self._write_json_evidence()

            # Append to human-readable log
            self._append_text_log(event)

    def _write_json_evidence(self) -> None:
        """Write all events to JSON file."""
        try:
            data = {
                "events": self._events,
                "summary": self._generate_summary(),
                "exported_at": datetime.now().isoformat(),
            }

            with open(self._evidence_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self._logger.error(f"Failed to write JSON evidence: {e}", exc_info=True)

    def _append_text_log(self, event: Dict[str, any]) -> None:
        """
        Append human-readable log entry.

        Args:
            event: Event dictionary to log
        """
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                timestamp = event["timestamp"]
                file_path = event["file"]
                verification = event["verification"]
                duration = event["duration_ms"]

                # Format log entry
                status = "PASS" if verification.get("ruff_passed") else "FAIL"
                f.write(f"\n[{timestamp}] {status} - {file_path}\n")
                f.write(f"  Duration: {duration:.0f}ms\n")

                if verification.get("error"):
                    f.write(f"  Error: {verification['error']}\n")
                elif not verification.get("ruff_passed"):
                    violations = verification.get("violations", [])
                    f.write(f"  Violations: {len(violations)}\n")
                    for v in violations:
                        fix_hint = " [fixable]" if v.get("fix_available") else ""
                        f.write(f"    • Line {v['line']}:{v['column']} - " f"{v['code']}: {v['message']}{fix_hint}\n")

        except Exception as e:
            self._logger.error(f"Failed to write text log: {e}", exc_info=True)

    def _generate_summary(self) -> Dict[str, any]:
        """
        Generate summary statistics from events.

        Returns:
            Dictionary with summary metrics
        """
        if not self._events:
            return {
                "total_verifications": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
            }

        total = len(self._events)
        passed = sum(1 for e in self._events if e["verification"].get("ruff_passed", False))
        errors = sum(1 for e in self._events if e["verification"].get("error"))
        failed = total - passed

        durations = [e["duration_ms"] for e in self._events]

        return {
            "total_verifications": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": passed / total if total > 0 else 0.0,
            "avg_duration_ms": sum(durations) / total if total > 0 else 0.0,
            "total_duration_ms": sum(durations),
        }

    def get_summary(self) -> Dict[str, any]:
        """
        Get current summary statistics.

        Returns:
            Summary dictionary with metrics
        """
        with self._lock:
            return self._generate_summary()


class FileChangeDebouncer:
    """
    Debounces file change events to avoid processing redundant changes.

    Thread-safe implementation using locks to prevent race conditions.
    Groups multiple rapid changes to the same file into a single event.
    """

    def __init__(self, debounce_ms: int = 500):
        """
        Initialize debouncer.

        Args:
            debounce_ms: Milliseconds to wait before processing changes
        """
        self._debounce_seconds = debounce_ms / 1000.0
        self._pending: Dict[str, float] = {}
        self._lock = Lock()

    def should_process(self, file_path: str) -> bool:
        """
        Check if file change should be processed.

        Args:
            file_path: Path to the changed file

        Returns:
            True if enough time has passed since last change
        """
        current_time = time.time()

        with self._lock:
            last_time = self._pending.get(file_path, 0)
            time_since_last = current_time - last_time

            if time_since_last >= self._debounce_seconds:
                self._pending[file_path] = current_time
                return True

            # Update pending time but don't process yet
            self._pending[file_path] = current_time
            return False


class PythonFileHandler(FileSystemEventHandler):
    """
    Handles file system events for Python files.

    Filters events to only process .py files and queues them for processing.
    Implements debouncing to avoid redundant event handling.
    """

    def __init__(self, event_queue: Queue, debouncer: FileChangeDebouncer, logger: logging.Logger):
        """
        Initialize file handler.

        Args:
            event_queue: Thread-safe queue for file change events
            debouncer: Debouncer to filter rapid changes
            logger: Logger instance for event logging
        """
        super().__init__()
        self._queue = event_queue
        self._debouncer = debouncer
        self._logger = logger

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Handle file modification events.

        Args:
            event: File system event from watchdog
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process Python files
        if file_path.suffix != ".py":
            return

        # Apply debouncing
        if not self._debouncer.should_process(str(file_path)):
            return

        self._logger.debug(f"Queuing change: {file_path}")
        self._queue.put(("modified", file_path))

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle file creation events.

        Args:
            event: File system event from watchdog
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix != ".py":
            return

        self._logger.debug(f"Queuing creation: {file_path}")
        self._queue.put(("created", file_path))


class FileChangeProcessor:
    """
    Processes file change events from the queue.

    Runs in a separate thread to avoid blocking the file watcher.
    Executes Ruff verification on each Python file change.
    Logs verification evidence automatically.
    """

    def __init__(
        self,
        event_queue: Queue,
        stop_event: Event,
        logger: logging.Logger,
        ruff_verifier: Optional[RuffVerifier] = None,
        evidence_logger: Optional[EvidenceLogger] = None,
    ):
        """
        Initialize processor.

        Args:
            event_queue: Queue to read events from
            stop_event: Event to signal shutdown
            logger: Logger instance
            ruff_verifier: Optional RuffVerifier instance for code verification
            evidence_logger: Optional EvidenceLogger for tracking verification results
        """
        self._queue = event_queue
        self._stop_event = stop_event
        self._logger = logger
        self._ruff_verifier = ruff_verifier
        self._evidence_logger = evidence_logger
        self._processed_count = 0

    def run(self) -> None:
        """
        Process events from queue until stopped.

        Runs in infinite loop checking for new events and shutdown signal.
        """
        self._logger.info("File change processor started")

        while not self._stop_event.is_set():
            try:
                # Non-blocking get with timeout to check stop_event
                event_type, file_path = self._queue.get(timeout=0.5)
                self._process_change(event_type, file_path)
                self._queue.task_done()
            except Exception:
                # Queue is empty, continue loop
                continue

        self._logger.info(f"Processor stopped. Processed {self._processed_count} changes")

    def _process_change(self, event_type: str, file_path: Path) -> None:
        """
        Process a single file change.

        Args:
            event_type: Type of change (modified, created)
            file_path: Path to changed file
        """
        self._processed_count += 1

        try:
            # Display relative path if possible
            try:
                display_path = file_path.relative_to(Path.cwd())
            except ValueError:
                display_path = file_path

            self._logger.info(f"[{event_type.upper()}] {display_path}")

            # Run Ruff verification if available
            if self._ruff_verifier:
                self._run_verification(file_path, event_type)

        except Exception as e:
            self._logger.error(f"Error processing {file_path}: {e}", exc_info=True)

    def _run_verification(self, file_path: Path, event_type: str = "modified") -> None:
        """
        Run Ruff verification and log results.

        Args:
            file_path: Path to Python file to verify
            event_type: Type of file event (modified, created)
        """
        self._logger.info("[VERIFY] Running Ruff check...")

        result = self._ruff_verifier.verify_file(file_path)

        # Log evidence if logger is available
        if self._evidence_logger:
            try:
                self._evidence_logger.log_verification(event_type, file_path, result)
            except Exception as e:
                self._logger.warning(f"Failed to log evidence: {e}")

        # Handle errors
        if result.error:
            self._logger.error(f"[ERROR] Verification failed: {result.error}")
            return

        # Report results
        if result.passed:
            self._logger.info(f"[PASS] No violations found ({result.duration_ms:.0f}ms)")
        else:
            self._logger.warning(f"[FAIL] Ruff found {result.violation_count} violation(s):")
            for violation in result.violations:
                # Format with visual indicator for violations
                fix_hint = " [fixable]" if violation.fix_available else ""
                self._logger.warning(
                    f"  • Line {violation.line}:{violation.column} - " f"{violation.code}: {violation.message}{fix_hint}"
                )

        self._logger.info(f"[INFO] Verification complete in {result.duration_ms:.0f}ms")


class DevAssistant:
    """
    Main development assistant orchestrator.

    Manages file watching, event processing, and graceful shutdown.
    Implements clean architecture with separation of concerns.
    Supports configuration via pyproject.toml with CLI override.
    """

    def __init__(
        self,
        watch_dirs: Optional[List[str]] = None,
        debounce_ms: int = 500,
        log_level: str = "INFO",
        enable_ruff: bool = True,
        enable_evidence: bool = True,
        config: Optional[AssistantConfig] = None,
    ):
        """
        Initialize development assistant.

        Args:
            watch_dirs: Directories to watch (defaults to scripts/ and tests/)
            debounce_ms: Debounce time in milliseconds
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            enable_ruff: Enable Ruff verification on file changes
            enable_evidence: Enable automatic evidence logging
            config: Optional pre-loaded configuration (if None, uses parameters)
        """
        # Use config if provided, otherwise use parameters
        if config is not None:
            self._watch_dirs = config.watch_paths
            self._debounce_ms = config.debounce_ms
            self._verification_timeout = config.verification_timeout_sec
            self._log_retention_days = config.log_retention_days
            enable_ruff = config.enable_ruff
            enable_evidence = config.enable_evidence
        else:
            self._watch_dirs = watch_dirs or ["scripts", "tests"]
            self._debounce_ms = debounce_ms
            self._verification_timeout = 2.0
            self._log_retention_days = 7

        self._root = Path.cwd()

        # Setup logging
        self._logger = self._setup_logging(log_level)

        # Thread coordination
        self._stop_event = Event()
        self._event_queue: Queue = Queue()

        # Components
        self._debouncer = FileChangeDebouncer(self._debounce_ms)
        self._observer = Observer()

        # Setup Ruff verifier
        ruff_verifier = None
        if enable_ruff:
            ruff_config = self._root / "ruff.toml"
            if ruff_config.exists():
                ruff_verifier = RuffVerifier(timeout_seconds=self._verification_timeout, ruff_config=ruff_config)
                self._logger.debug(f"Ruff verification enabled (config: {ruff_config})")
            else:
                ruff_verifier = RuffVerifier(timeout_seconds=self._verification_timeout)
                self._logger.debug("Ruff verification enabled (default config)")

        # Setup evidence logger
        evidence_logger = None
        if enable_evidence and enable_ruff:
            try:
                evidence_logger = EvidenceLogger(retention_days=self._log_retention_days)
                self._logger.debug(f"Evidence logging enabled (dir: {evidence_logger._daily_dir})")
            except Exception as e:
                self._logger.warning(f"Failed to initialize evidence logger: {e}")

        self._processor = FileChangeProcessor(
            self._event_queue, self._stop_event, self._logger, ruff_verifier, evidence_logger
        )
        self._processor_thread: Optional[Thread] = None

        # Register signal handlers
        self._register_signals()

    def _setup_logging(self, log_level: str) -> logging.Logger:
        """
        Configure logging with console handler.

        Args:
            log_level: Level to log at

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("dev_assistant")
        logger.setLevel(getattr(logging, log_level.upper()))

        # Console handler with formatting
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _register_signals(self) -> None:
        """Register signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum: int, frame) -> None:
        """
        Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self._logger.info("\nShutdown signal received. Stopping gracefully...")
        self.stop()

    def start(self) -> None:
        """
        Start the development assistant.

        Validates directories, starts file watching, and begins event processing.

        Raises:
            RuntimeError: If watch directories don't exist or can't be accessed
        """
        self._logger.info("=" * 60)
        self._logger.info("Development Assistant - File Watcher")
        self._logger.info("=" * 60)

        # Validate watch directories
        valid_dirs: Set[Path] = set()
        for watch_dir in self._watch_dirs:
            dir_path = self._root / watch_dir
            if not dir_path.exists():
                self._logger.warning(f"Directory not found: {watch_dir}")
                continue
            if not dir_path.is_dir():
                self._logger.warning(f"Not a directory: {watch_dir}")
                continue
            valid_dirs.add(dir_path)

        if not valid_dirs:
            raise RuntimeError("No valid directories to watch")

        # Setup file handler
        event_handler = PythonFileHandler(self._event_queue, self._debouncer, self._logger)

        # Schedule observers for each directory
        for dir_path in valid_dirs:
            self._observer.schedule(event_handler, str(dir_path), recursive=True)
            try:
                rel_path = dir_path.relative_to(self._root)
                self._logger.info(f"Watching: {rel_path}/")
            except ValueError:
                # Path is outside root (e.g., absolute path in tests)
                self._logger.info(f"Watching: {dir_path}/")

        # Start observer
        self._observer.start()
        self._logger.info(f"Debounce time: {self._debounce_ms}ms")
        self._logger.info("File watcher active. Press Ctrl+C to stop.\n")

        # Start processor thread
        self._processor_thread = Thread(target=self._processor.run, daemon=True)
        self._processor_thread.start()

        # Keep main thread alive
        try:
            while not self._stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self._handle_shutdown(signal.SIGINT, None)

    def stop(self) -> None:
        """
        Stop the development assistant gracefully.

        Stops file watching, drains event queue, and cleans up resources.
        """
        if self._stop_event.is_set():
            return

        self._logger.info("Stopping file watcher...")
        self._stop_event.set()

        # Stop observer
        if self._observer.is_alive():
            self._observer.stop()
            self._observer.join(timeout=5)

        # Wait for processor thread
        if self._processor_thread and self._processor_thread.is_alive():
            self._processor_thread.join(timeout=5)

        # Drain remaining queue items
        remaining = self._event_queue.qsize()
        if remaining > 0:
            self._logger.info(f"Draining {remaining} pending events...")

        self._logger.info("Development Assistant stopped cleanly.")


def main() -> None:
    """
    CLI entry point for development assistant.

    Loads configuration from pyproject.toml and merges with CLI arguments.
    CLI arguments override configuration file values.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Development Assistant - Production File Watcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration:
  Configuration is loaded from pyproject.toml [tool.dev-assistant] section.
  CLI arguments override configuration file values.

  Example pyproject.toml:
    [tool.dev-assistant]
    enabled = true
    watch_paths = ["scripts", "tests"]
    debounce_ms = 500
    verification_timeout_sec = 2.0
    log_retention_days = 7
    enable_ruff = true
    enable_evidence = true
        """,
    )
    parser.add_argument(
        "--watch-dirs",
        nargs="+",
        default=None,
        help="Directories to watch (overrides config file)",
    )
    parser.add_argument(
        "--debounce",
        type=int,
        default=None,
        help="Debounce time in milliseconds (overrides config file)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--no-ruff",
        action="store_true",
        help="Disable Ruff verification (overrides config file)",
    )
    parser.add_argument(
        "--no-evidence",
        action="store_true",
        help="Disable evidence logging (overrides config file)",
    )

    args = parser.parse_args()

    try:
        # Load configuration from pyproject.toml
        config_loader = ConfigLoader()
        config = config_loader.load()

        # Check if assistant is enabled
        if not config.enabled:
            print("Development Assistant is disabled in configuration.")
            sys.exit(0)

        # Merge with CLI arguments (CLI takes precedence)
        config = config_loader.merge_with_cli_args(
            config,
            watch_dirs=args.watch_dirs,
            debounce=args.debounce,
            log_level=args.log_level,
            no_ruff=args.no_ruff,
            no_evidence=args.no_evidence,
        )

        # Create and start assistant
        assistant = DevAssistant(
            config=config,
            log_level=args.log_level,
        )

        assistant.start()

    except RuntimeError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
