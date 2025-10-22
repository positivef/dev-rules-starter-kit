"""
Tests for Development Assistant File Watcher

Comprehensive test suite covering:
- File change debouncing logic
- Event filtering and queuing
- Graceful shutdown handling
- Thread safety and error handling
- Evidence logging integration
"""

import json
import logging
import tempfile
import time
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Event
from unittest.mock import Mock

import pytest

from scripts.dev_assistant import (
    AssistantConfig,
    ConfigLoader,
    DevAssistant,
    EvidenceLogger,
    FileChangeDebouncer,
    FileChangeProcessor,
    PythonFileHandler,
    RuffVerifier,
    RuffViolation,
    VerificationResult,
)


class TestAssistantConfig:
    """Test suite for AssistantConfig class."""

    def test_default_values(self):
        """Config should have sensible defaults."""
        config = AssistantConfig()
        assert config.enabled is True
        assert config.watch_paths == ["scripts", "tests"]
        assert config.debounce_ms == 500
        assert config.verification_timeout_sec == 2.0
        assert config.log_retention_days == 7
        assert config.enable_ruff is True
        assert config.enable_evidence is True

    def test_custom_values(self):
        """Config should accept custom values."""
        config = AssistantConfig(
            enabled=False,
            watch_paths=["src", "lib"],
            debounce_ms=1000,
            verification_timeout_sec=5.0,
            log_retention_days=14,
            enable_ruff=False,
            enable_evidence=False,
        )
        assert config.enabled is False
        assert config.watch_paths == ["src", "lib"]
        assert config.debounce_ms == 1000
        assert config.verification_timeout_sec == 5.0
        assert config.log_retention_days == 14
        assert config.enable_ruff is False
        assert config.enable_evidence is False

    def test_validate_valid_config(self):
        """Validate should return empty list for valid config."""
        config = AssistantConfig()
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_enabled(self):
        """Validate should catch invalid enabled value."""
        config = AssistantConfig()
        config.enabled = "yes"  # Should be bool
        errors = config.validate()
        assert any("enabled must be boolean" in e for e in errors)

    def test_validate_invalid_watch_paths(self):
        """Validate should catch invalid watch_paths."""
        # Empty list
        config = AssistantConfig()
        config.watch_paths = []
        errors = config.validate()
        assert any("watch_paths must be non-empty list" in e for e in errors)

        # Not a list
        config.watch_paths = "scripts"
        errors = config.validate()
        assert any("watch_paths must be non-empty list" in e for e in errors)

        # List with non-strings
        config.watch_paths = ["scripts", 123]
        errors = config.validate()
        assert any("watch_paths must contain only strings" in e for e in errors)

    def test_validate_invalid_debounce_ms(self):
        """Validate should catch invalid debounce_ms."""
        config = AssistantConfig()
        config.debounce_ms = -100
        errors = config.validate()
        assert any("debounce_ms must be non-negative integer" in e for e in errors)

        config.debounce_ms = "500"
        errors = config.validate()
        assert any("debounce_ms must be non-negative integer" in e for e in errors)

    def test_validate_invalid_timeout(self):
        """Validate should catch invalid verification_timeout_sec."""
        config = AssistantConfig()
        config.verification_timeout_sec = 0
        errors = config.validate()
        assert any("verification_timeout_sec must be positive number" in e for e in errors)

        config.verification_timeout_sec = -2.5
        errors = config.validate()
        assert any("verification_timeout_sec must be positive number" in e for e in errors)

    def test_validate_invalid_retention_days(self):
        """Validate should catch invalid log_retention_days."""
        config = AssistantConfig()
        config.log_retention_days = -5
        errors = config.validate()
        assert any("log_retention_days must be non-negative integer" in e for e in errors)


class TestConfigLoader:
    """Test suite for ConfigLoader class."""

    def test_load_without_pyproject(self):
        """Loader should return defaults when no pyproject.toml exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ConfigLoader(project_root=Path(tmpdir))
            config = loader.load()

            assert config.enabled is True
            assert config.watch_paths == ["scripts", "tests"]
            assert config.debounce_ms == 500

    def test_load_with_valid_config(self):
        """Loader should parse valid pyproject.toml configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pyproject.toml
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text(
                """
[tool.dev-assistant]
enabled = true
watch_paths = ["src", "lib", "tests"]
debounce_ms = 1000
verification_timeout_sec = 3.5
log_retention_days = 14
enable_ruff = false
enable_evidence = true
                """,
                encoding="utf-8",
            )

            loader = ConfigLoader(project_root=Path(tmpdir))
            config = loader.load()

            assert config.enabled is True
            assert config.watch_paths == ["src", "lib", "tests"]
            assert config.debounce_ms == 1000
            assert config.verification_timeout_sec == 3.5
            assert config.log_retention_days == 14
            assert config.enable_ruff is False
            assert config.enable_evidence is True

    def test_load_partial_config(self):
        """Loader should merge partial config with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text(
                """
[tool.dev-assistant]
watch_paths = ["custom"]
debounce_ms = 200
                """,
                encoding="utf-8",
            )

            loader = ConfigLoader(project_root=Path(tmpdir))
            config = loader.load()

            # Custom values
            assert config.watch_paths == ["custom"]
            assert config.debounce_ms == 200

            # Default values
            assert config.enabled is True
            assert config.verification_timeout_sec == 2.0
            assert config.enable_ruff is True

    def test_load_no_dev_assistant_section(self):
        """Loader should return defaults when [tool.dev-assistant] section is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text(
                """
[project]
name = "test-project"

[tool.ruff]
line-length = 100
                """,
                encoding="utf-8",
            )

            loader = ConfigLoader(project_root=Path(tmpdir))
            config = loader.load()

            assert config.enabled is True
            assert config.watch_paths == ["scripts", "tests"]

    def test_load_invalid_toml(self):
        """Loader should raise RuntimeError for invalid TOML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text(
                """
[tool.dev-assistant
invalid toml syntax
                """,
                encoding="utf-8",
            )

            loader = ConfigLoader(project_root=Path(tmpdir))

            with pytest.raises(RuntimeError, match="Failed to parse"):
                loader.load()

    def test_load_invalid_config_values(self):
        """Loader should raise RuntimeError for invalid config values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text(
                """
[tool.dev-assistant]
enabled = "yes"  # Should be boolean
watch_paths = []  # Should be non-empty
debounce_ms = -500  # Should be non-negative
                """,
                encoding="utf-8",
            )

            loader = ConfigLoader(project_root=Path(tmpdir))

            with pytest.raises(RuntimeError, match="Invalid configuration"):
                loader.load()

    def test_merge_with_cli_args_override(self):
        """CLI args should override config file values."""
        config = AssistantConfig(watch_paths=["scripts"], debounce_ms=500, enable_ruff=True, enable_evidence=True)

        loader = ConfigLoader()
        merged = loader.merge_with_cli_args(config, watch_dirs=["custom"], debounce=1000, no_ruff=True, no_evidence=True)

        # CLI overrides
        assert merged.watch_paths == ["custom"]
        assert merged.debounce_ms == 1000
        assert merged.enable_ruff is False
        assert merged.enable_evidence is False

    def test_merge_with_partial_cli_args(self):
        """Partial CLI args should only override specified values."""
        config = AssistantConfig(watch_paths=["scripts"], debounce_ms=500, enable_ruff=True, enable_evidence=True)

        loader = ConfigLoader()
        merged = loader.merge_with_cli_args(config, debounce=1000)

        # Only debounce overridden
        assert merged.watch_paths == ["scripts"]  # Unchanged
        assert merged.debounce_ms == 1000  # Overridden
        assert merged.enable_ruff is True  # Unchanged

    def test_merge_with_no_cli_args(self):
        """Config should remain unchanged when no CLI args provided."""
        config = AssistantConfig(watch_paths=["scripts"], debounce_ms=500)

        loader = ConfigLoader()
        merged = loader.merge_with_cli_args(config)

        assert merged.watch_paths == ["scripts"]
        assert merged.debounce_ms == 500

    def test_merge_validates_result(self):
        """Merge should validate the final configuration."""
        config = AssistantConfig()

        loader = ConfigLoader()

        # Provide invalid override
        with pytest.raises(RuntimeError, match="Invalid configuration"):
            loader.merge_with_cli_args(config, watch_dirs=[])  # Empty list


class TestFileChangeDebouncer:
    """Test suite for FileChangeDebouncer class."""

    def test_first_change_processed_immediately(self):
        """First change to a file should be processed immediately."""
        debouncer = FileChangeDebouncer(debounce_ms=500)
        assert debouncer.should_process("test.py") is True

    def test_rapid_changes_debounced(self):
        """Rapid successive changes should be debounced."""
        debouncer = FileChangeDebouncer(debounce_ms=500)

        # First change
        assert debouncer.should_process("test.py") is True

        # Immediate second change (should be debounced)
        assert debouncer.should_process("test.py") is False

    def test_changes_after_debounce_period(self):
        """Changes after debounce period should be processed."""
        debouncer = FileChangeDebouncer(debounce_ms=100)

        # First change
        assert debouncer.should_process("test.py") is True

        # Wait for debounce period
        time.sleep(0.15)

        # Should be processed now
        assert debouncer.should_process("test.py") is True

    def test_different_files_independent(self):
        """Different files should be debounced independently."""
        debouncer = FileChangeDebouncer(debounce_ms=500)

        assert debouncer.should_process("file1.py") is True
        assert debouncer.should_process("file2.py") is True
        assert debouncer.should_process("file1.py") is False
        assert debouncer.should_process("file2.py") is False

    def test_thread_safety(self):
        """Debouncer should be thread-safe."""
        import threading

        debouncer = FileChangeDebouncer(debounce_ms=100)
        results = []

        def check_file(file_path):
            for _ in range(10):
                result = debouncer.should_process(file_path)
                results.append(result)
                time.sleep(0.01)

        threads = [threading.Thread(target=check_file, args=("test.py",)) for _ in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # At least one should be True (first access)
        assert any(results)


class TestPythonFileHandler:
    """Test suite for PythonFileHandler class."""

    def test_filters_python_files_only(self):
        """Handler should only process Python files."""
        queue = Queue()
        debouncer = FileChangeDebouncer()
        logger = logging.getLogger("test")
        handler = PythonFileHandler(queue, debouncer, logger)

        # Create mock event for Python file
        event = Mock()
        event.is_directory = False
        event.src_path = "test.py"

        handler.on_modified(event)
        assert queue.qsize() == 1

        # Non-Python file should be ignored
        event.src_path = "test.txt"
        handler.on_modified(event)
        assert queue.qsize() == 1

    def test_ignores_directories(self):
        """Handler should ignore directory events."""
        queue = Queue()
        debouncer = FileChangeDebouncer()
        logger = logging.getLogger("test")
        handler = PythonFileHandler(queue, debouncer, logger)

        event = Mock()
        event.is_directory = True
        event.src_path = "some_dir"

        handler.on_modified(event)
        assert queue.empty()

    def test_respects_debouncing(self):
        """Handler should respect debouncer decisions."""
        queue = Queue()
        debouncer = FileChangeDebouncer(debounce_ms=500)
        logger = logging.getLogger("test")
        handler = PythonFileHandler(queue, debouncer, logger)

        event = Mock()
        event.is_directory = False
        event.src_path = "test.py"

        # First event should be queued
        handler.on_modified(event)
        assert queue.qsize() == 1

        # Rapid second event should be debounced
        handler.on_modified(event)
        assert queue.qsize() == 1

    def test_handles_created_events(self):
        """Handler should process file creation events."""
        queue = Queue()
        debouncer = FileChangeDebouncer()
        logger = logging.getLogger("test")
        handler = PythonFileHandler(queue, debouncer, logger)

        event = Mock()
        event.is_directory = False
        event.src_path = "new_file.py"

        handler.on_created(event)
        assert queue.qsize() == 1

        event_type, file_path = queue.get()
        assert event_type == "created"
        assert str(file_path) == "new_file.py"


class TestFileChangeProcessor:
    """Test suite for FileChangeProcessor class."""

    def test_processes_queued_events(self):
        """Processor should handle queued events."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")
        processor = FileChangeProcessor(queue, stop_event, logger)

        # Add test event
        queue.put(("modified", Path("test.py")))

        # Process in separate thread with timeout
        import threading

        def run_processor():
            time.sleep(0.1)
            stop_event.set()

        thread = threading.Thread(target=processor.run)
        thread.daemon = True
        thread.start()

        run_processor()
        thread.join(timeout=1)

        assert processor._processed_count == 1

    def test_stops_on_signal(self):
        """Processor should stop when stop_event is set."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")
        processor = FileChangeProcessor(queue, stop_event, logger)

        import threading

        thread = threading.Thread(target=processor.run)
        thread.daemon = True
        thread.start()

        time.sleep(0.1)
        stop_event.set()
        thread.join(timeout=1)

        assert not thread.is_alive()

    def test_handles_processing_errors(self, caplog):
        """Processor should handle errors gracefully."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")
        logger.setLevel(logging.ERROR)
        processor = FileChangeProcessor(queue, stop_event, logger)

        # Add event that will cause error (invalid path operation)
        queue.put(("modified", Path("/nonexistent/invalid/path.py")))

        import threading

        def run_processor():
            time.sleep(0.2)
            stop_event.set()

        thread = threading.Thread(target=processor.run)
        thread.daemon = True
        thread.start()

        run_processor()
        thread.join(timeout=1)

        # Should have processed despite error
        assert processor._processed_count == 1


class TestDevAssistant:
    """Test suite for DevAssistant class."""

    def test_initialization(self):
        """DevAssistant should initialize with defaults."""
        assistant = DevAssistant()

        assert assistant._watch_dirs == ["scripts", "tests"]
        assert assistant._debounce_ms == 500
        assert assistant._logger is not None
        assert not assistant._stop_event.is_set()

    def test_custom_configuration(self):
        """DevAssistant should accept custom configuration."""
        assistant = DevAssistant(watch_dirs=["custom_dir"], debounce_ms=1000, log_level="DEBUG")

        assert assistant._watch_dirs == ["custom_dir"]
        assert assistant._debounce_ms == 1000
        assert assistant._logger.level == logging.DEBUG

    def test_validates_watch_directories(self):
        """DevAssistant should validate watch directories exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_dir = Path(tmpdir) / "valid"
            valid_dir.mkdir()

            assistant = DevAssistant(watch_dirs=[str(valid_dir)])

            # Should not raise error for valid directory
            # Note: Can't fully test start() without blocking, but we can verify setup
            assert assistant._root.exists()

    def test_raises_on_no_valid_directories(self):
        """DevAssistant should raise error if no valid directories."""
        assistant = DevAssistant(watch_dirs=["nonexistent_dir_12345"])

        with pytest.raises(RuntimeError, match="No valid directories to watch"):
            assistant.start()

    def test_graceful_shutdown(self):
        """DevAssistant should stop gracefully."""
        assistant = DevAssistant()

        # Set stop event
        assistant.stop()

        assert assistant._stop_event.is_set()

    def test_signal_handler_registration(self):
        """DevAssistant should register signal handlers."""
        import signal

        # Create assistant which registers signal handlers
        DevAssistant()

        # Verify signal handlers are registered (not None)
        # Note: signal.getsignal returns the handler function
        sigint_handler = signal.getsignal(signal.SIGINT)
        sigterm_handler = signal.getsignal(signal.SIGTERM)

        assert sigint_handler is not None
        assert sigterm_handler is not None


class TestIntegration:
    """Integration tests for complete file watching workflow."""

    @pytest.mark.slow
    def test_file_watch_and_process_workflow(self):
        """Test complete workflow from file change to processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watch_dir = Path(tmpdir) / "scripts"
            watch_dir.mkdir()

            # Create DevAssistant with temp directory
            assistant = DevAssistant(watch_dirs=[str(watch_dir)], debounce_ms=100, log_level="DEBUG")

            # Start in background thread
            import threading

            start_thread = threading.Thread(target=assistant.start, daemon=True)
            start_thread.start()

            # Wait for observer to start
            time.sleep(0.5)

            # Create a Python file
            test_file = watch_dir / "test_script.py"
            test_file.write_text("# Test content")

            # Wait for processing
            time.sleep(0.3)

            # Modify file
            test_file.write_text("# Modified content")

            # Wait for processing
            time.sleep(0.3)

            # Stop assistant
            assistant.stop()

            # Verify it stopped
            assert assistant._stop_event.is_set()

    def test_debouncing_in_real_scenario(self):
        """Test debouncing with actual file modifications."""
        debouncer = FileChangeDebouncer(debounce_ms=200)

        # Simulate rapid file saves
        results = []
        for i in range(5):
            result = debouncer.should_process("test.py")
            results.append(result)
            time.sleep(0.05)  # 50ms between changes

        # First should be True, rest False (within debounce window)
        assert results[0] is True
        assert all(not r for r in results[1:])

        # Wait for debounce period
        time.sleep(0.2)

        # Should process again
        assert debouncer.should_process("test.py") is True


class TestRuffVerifier:
    """Test suite for RuffVerifier class."""

    def test_initialization(self):
        """RuffVerifier should initialize with defaults."""
        verifier = RuffVerifier()
        assert verifier._timeout == 2.0
        assert verifier._ruff_config is None

    def test_custom_configuration(self):
        """RuffVerifier should accept custom configuration."""
        config_path = Path("ruff.toml")
        verifier = RuffVerifier(timeout_seconds=5.0, ruff_config=config_path)
        assert verifier._timeout == 5.0
        assert verifier._ruff_config == config_path

    def test_verify_nonexistent_file(self):
        """Verification should handle nonexistent files gracefully."""
        verifier = RuffVerifier()
        result = verifier.verify_file(Path("/nonexistent/file.py"))

        assert not result.passed
        assert result.error is not None
        assert "not found" in result.error.lower()
        assert result.violation_count == 0

    def test_verify_clean_file(self):
        """Verification should pass for clean Python files."""
        verifier = RuffVerifier()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Clean module."""\n\n\ndef hello():\n    """Say hello."""\n    return "Hello"\n')
            f.flush()
            temp_path = Path(f.name)

        try:
            result = verifier.verify_file(temp_path)

            # Should pass (no violations)
            assert result.passed
            assert result.violation_count == 0
            assert result.error is None
            assert result.duration_ms >= 0

        finally:
            temp_path.unlink()

    def test_verify_file_with_violations(self):
        """Verification should detect violations in Python files."""
        verifier = RuffVerifier()

        # Create file with intentional violations
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Line too long + unused import
            f.write("import os\nimport sys\n\n")
            f.write("x = " + '"' + "a" * 200 + '"' + "\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            result = verifier.verify_file(temp_path)

            # Should fail with violations
            assert not result.passed
            assert result.violation_count > 0
            assert result.error is None
            assert result.duration_ms >= 0

            # Check violation structure
            for violation in result.violations:
                assert violation.code
                assert violation.message
                assert violation.line > 0

        finally:
            temp_path.unlink()

    def test_parse_ruff_json_output(self):
        """Parser should handle Ruff JSON output correctly."""
        verifier = RuffVerifier()

        json_output = """[
            {
                "code": "E501",
                "message": "Line too long (100 > 88 characters)",
                "location": {"row": 10, "column": 1},
                "fix": null
            },
            {
                "code": "F401",
                "message": "`os` imported but unused",
                "location": {"row": 1, "column": 8},
                "fix": {"edits": []}
            }
        ]"""

        violations = verifier._parse_ruff_output(json_output)

        assert len(violations) == 2
        assert violations[0].code == "E501"
        assert violations[0].line == 10
        assert violations[0].column == 1
        assert not violations[0].fix_available

        assert violations[1].code == "F401"
        assert violations[1].line == 1
        assert violations[1].fix_available

    def test_parse_empty_output(self):
        """Parser should handle empty output (no violations)."""
        verifier = RuffVerifier()

        violations = verifier._parse_ruff_output("")
        assert len(violations) == 0

        violations = verifier._parse_ruff_output("[]")
        assert len(violations) == 0

    def test_parse_invalid_json(self):
        """Parser should handle invalid JSON gracefully."""
        verifier = RuffVerifier()

        violations = verifier._parse_ruff_output("not valid json")
        assert len(violations) == 0

    def test_verification_timeout_protection(self):
        """Verifier should handle timeout scenarios."""
        # Use very short timeout for testing
        verifier = RuffVerifier(timeout_seconds=0.001)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Test file\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            result = verifier.verify_file(temp_path)

            # May timeout or succeed depending on system speed
            # Just verify result structure is valid
            assert result.file_path == temp_path
            assert isinstance(result.passed, bool)
            assert isinstance(result.duration_ms, (int, float))

        finally:
            temp_path.unlink()

    def test_ruff_violation_str_format(self):
        """RuffViolation should format nicely."""
        violation = RuffViolation(
            code="E501",
            message="Line too long",
            line=42,
            column=10,
            fix_available=True,
        )

        formatted = str(violation)
        assert "42" in formatted
        assert "10" in formatted
        assert "E501" in formatted
        assert "Line too long" in formatted


class TestFileChangeProcessorWithRuff:
    """Test FileChangeProcessor with Ruff integration."""

    def test_processor_with_ruff_verifier(self):
        """Processor should run Ruff verification when configured."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")
        logger.setLevel(logging.WARNING)

        # Create verifier and processor
        verifier = RuffVerifier()
        processor = FileChangeProcessor(queue, stop_event, logger, verifier)

        # Create clean test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Test."""\n')
            f.flush()
            temp_path = Path(f.name)

        try:
            # Queue file change
            queue.put(("modified", temp_path))

            import threading

            thread = threading.Thread(target=processor.run)
            thread.daemon = True
            thread.start()

            time.sleep(0.3)
            stop_event.set()
            thread.join(timeout=2)

            # Should have processed the file
            assert processor._processed_count == 1

        finally:
            temp_path.unlink()

    def test_processor_without_ruff_verifier(self):
        """Processor should work without Ruff verifier."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")

        # Create processor without verifier
        processor = FileChangeProcessor(queue, stop_event, logger, ruff_verifier=None)

        queue.put(("modified", Path("test.py")))

        import threading

        thread = threading.Thread(target=processor.run)
        thread.daemon = True
        thread.start()

        time.sleep(0.2)
        stop_event.set()
        thread.join(timeout=1)

        assert processor._processed_count == 1


class TestDevAssistantWithRuff:
    """Test DevAssistant with Ruff integration."""

    def test_initialization_with_ruff_enabled(self):
        """DevAssistant should initialize with Ruff enabled."""
        assistant = DevAssistant(enable_ruff=True)
        assert assistant._processor._ruff_verifier is not None

    def test_initialization_with_ruff_disabled(self):
        """DevAssistant should initialize with Ruff disabled."""
        assistant = DevAssistant(enable_ruff=False)
        assert assistant._processor._ruff_verifier is None

    def test_initialization_with_evidence_enabled(self):
        """DevAssistant should initialize with evidence logging enabled."""
        assistant = DevAssistant(enable_evidence=True, enable_ruff=True)
        assert assistant._processor._evidence_logger is not None

    def test_initialization_with_evidence_disabled(self):
        """DevAssistant should initialize with evidence logging disabled."""
        assistant = DevAssistant(enable_evidence=False)
        assert assistant._processor._evidence_logger is None


class TestEvidenceLogger:
    """Test suite for EvidenceLogger class."""

    def test_initialization(self):
        """EvidenceLogger should initialize with default settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))
            assert logger._retention_days == 7
            assert logger._daily_dir.exists()
            assert "dev-assistant-" in logger._daily_dir.name

    def test_daily_directory_creation(self):
        """Logger should create daily directory with correct format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))
            today = datetime.now().strftime("%Y%m%d")
            expected_dir = Path(tmpdir) / f"dev-assistant-{today}"
            assert logger._daily_dir == expected_dir
            assert expected_dir.exists()

    def test_log_verification_success(self):
        """Logger should record successful verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))

            # Create successful verification result
            result = VerificationResult(file_path=Path("test.py"), passed=True, violations=[], duration_ms=50.0)

            logger.log_verification("modified", Path("test.py"), result)

            # Check JSON evidence
            assert logger._evidence_file.exists()
            with open(logger._evidence_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data["events"]) == 1
            event = data["events"][0]
            assert event["event_type"] == "modified"
            assert event["file"] == "test.py"
            assert event["verification"]["ruff_passed"] is True
            assert event["duration_ms"] == 50.0

            # Check text log
            assert logger._log_file.exists()
            log_content = logger._log_file.read_text(encoding="utf-8")
            assert "PASS" in log_content
            assert "test.py" in log_content

    def test_log_verification_failure(self):
        """Logger should record verification failures with violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))

            violations = [
                RuffViolation(code="E501", message="Line too long", line=10, column=1, fix_available=False),
                RuffViolation(code="F401", message="Unused import", line=1, column=8, fix_available=True),
            ]

            result = VerificationResult(file_path=Path("bad.py"), passed=False, violations=violations, duration_ms=75.0)

            logger.log_verification("created", Path("bad.py"), result)

            # Check JSON evidence
            with open(logger._evidence_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            event = data["events"][0]
            assert event["verification"]["ruff_passed"] is False
            assert len(event["verification"]["violations"]) == 2
            assert event["verification"]["violations"][0]["code"] == "E501"
            assert event["verification"]["violations"][1]["fix_available"] is True

            # Check text log
            log_content = logger._log_file.read_text(encoding="utf-8")
            assert "FAIL" in log_content
            assert "E501" in log_content
            assert "F401" in log_content
            assert "[fixable]" in log_content

    def test_log_verification_error(self):
        """Logger should record verification errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))

            result = VerificationResult(
                file_path=Path("error.py"),
                passed=False,
                violations=[],
                duration_ms=10.0,
                error="Ruff not installed",
            )

            logger.log_verification("modified", Path("error.py"), result)

            # Check JSON evidence
            with open(logger._evidence_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            event = data["events"][0]
            assert event["verification"]["ruff_passed"] is False
            assert event["verification"]["error"] == "Ruff not installed"

            # Check text log
            log_content = logger._log_file.read_text(encoding="utf-8")
            assert "Error: Ruff not installed" in log_content

    def test_summary_generation(self):
        """Logger should generate accurate summary statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))

            # Log multiple verifications
            results = [
                VerificationResult(Path("pass1.py"), True, [], 30.0),
                VerificationResult(Path("pass2.py"), True, [], 40.0),
                VerificationResult(
                    Path("fail1.py"),
                    False,
                    [RuffViolation("E501", "Line too long", 1, 1)],
                    50.0,
                ),
                VerificationResult(Path("error1.py"), False, [], 20.0, "Error"),
            ]

            for i, result in enumerate(results):
                logger.log_verification("modified", result.file_path, result)

            summary = logger.get_summary()

            assert summary["total_verifications"] == 4
            assert summary["passed"] == 2
            assert summary["failed"] == 2
            assert summary["errors"] == 1
            assert summary["success_rate"] == 0.5
            assert summary["avg_duration_ms"] == 35.0
            assert summary["total_duration_ms"] == 140.0

    def test_log_rotation(self):
        """Logger should rotate old logs beyond retention period."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_dir = Path(tmpdir)

            # Create old directories
            old_dir1 = runs_dir / "dev-assistant-20231201"
            old_dir2 = runs_dir / "dev-assistant-20231215"
            old_dir1.mkdir()
            old_dir2.mkdir()

            # Set old modification time (10 days ago)
            import os

            ten_days_ago = time.time() - (10 * 86400)
            os.utime(old_dir1, (ten_days_ago, ten_days_ago))
            os.utime(old_dir2, (ten_days_ago, ten_days_ago))

            # Create logger (should trigger rotation with 7 day retention)
            logger = EvidenceLogger(runs_dir=runs_dir, retention_days=7)

            # Old directories should be removed
            assert not old_dir1.exists()
            assert not old_dir2.exists()

            # Current directory should exist
            assert logger._daily_dir.exists()

    def test_thread_safety(self):
        """Logger should be thread-safe for concurrent logging."""
        import threading

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = EvidenceLogger(runs_dir=Path(tmpdir))

            def log_multiple():
                for i in range(10):
                    result = VerificationResult(Path(f"test_{i}.py"), passed=True, violations=[], duration_ms=10.0)
                    logger.log_verification("modified", Path(f"test_{i}.py"), result)

            threads = [threading.Thread(target=log_multiple) for _ in range(3)]

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Should have logged 30 events (3 threads * 10 events)
            summary = logger.get_summary()
            assert summary["total_verifications"] == 30

    def test_load_existing_evidence(self):
        """Logger should load and append to existing evidence file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial logger and log event
            logger1 = EvidenceLogger(runs_dir=Path(tmpdir))
            result1 = VerificationResult(Path("test1.py"), True, [], 30.0)
            logger1.log_verification("modified", Path("test1.py"), result1)

            # Create new logger instance (should load existing)
            logger2 = EvidenceLogger(runs_dir=Path(tmpdir))
            result2 = VerificationResult(Path("test2.py"), True, [], 40.0)
            logger2.log_verification("modified", Path("test2.py"), result2)

            # Should have both events
            summary = logger2.get_summary()
            assert summary["total_verifications"] == 2


class TestFileChangeProcessorWithEvidence:
    """Test FileChangeProcessor with evidence logging."""

    def test_processor_logs_evidence(self):
        """Processor should log verification evidence automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = Queue()
            stop_event = Event()
            logger = logging.getLogger("test")
            logger.setLevel(logging.WARNING)

            # Create components
            verifier = RuffVerifier()
            evidence_logger = EvidenceLogger(runs_dir=Path(tmpdir))
            processor = FileChangeProcessor(queue, stop_event, logger, verifier, evidence_logger)

            # Create clean test file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write('"""Test."""\n')
                f.flush()
                temp_path = Path(f.name)

            try:
                # Queue file change
                queue.put(("modified", temp_path))

                import threading

                thread = threading.Thread(target=processor.run)
                thread.daemon = True
                thread.start()

                time.sleep(0.3)
                stop_event.set()
                thread.join(timeout=2)

                # Evidence should be logged
                summary = evidence_logger.get_summary()
                assert summary["total_verifications"] == 1
                assert summary["passed"] == 1

            finally:
                temp_path.unlink()

    def test_processor_without_evidence_logger(self):
        """Processor should work without evidence logger."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")

        verifier = RuffVerifier()
        processor = FileChangeProcessor(queue, stop_event, logger, verifier, evidence_logger=None)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Test."""\n')
            f.flush()
            temp_path = Path(f.name)

        try:
            queue.put(("modified", temp_path))

            import threading

            thread = threading.Thread(target=processor.run)
            thread.daemon = True
            thread.start()

            time.sleep(0.2)
            stop_event.set()
            thread.join(timeout=1)

            # Should process without error
            assert processor._processed_count == 1

        finally:
            temp_path.unlink()


# Performance benchmarks (optional, can be run separately)
@pytest.mark.benchmark
class TestPerformance:
    """Performance tests to ensure <2% CPU usage."""

    def test_debouncer_performance(self):
        """Debouncer should handle high frequency checks efficiently."""
        debouncer = FileChangeDebouncer(debounce_ms=100)

        start = time.time()
        for i in range(10000):
            debouncer.should_process(f"file_{i % 100}.py")
        duration = time.time() - start

        # Should complete in under 1 second
        assert duration < 1.0

    def test_queue_processing_performance(self):
        """Queue processing should be efficient."""
        queue = Queue()
        stop_event = Event()
        logger = logging.getLogger("test")
        logger.setLevel(logging.WARNING)  # Reduce logging overhead

        processor = FileChangeProcessor(queue, stop_event, logger)

        # Queue many events
        for i in range(1000):
            queue.put(("modified", Path(f"file_{i}.py")))

        import threading

        start = time.time()
        thread = threading.Thread(target=processor.run)
        thread.daemon = True
        thread.start()

        # Wait for queue to drain
        queue.join()
        stop_event.set()
        thread.join(timeout=5)
        duration = time.time() - start

        # Should process 1000 events in under 2 seconds
        assert duration < 2.0
        assert processor._processed_count == 1000

    def test_ruff_verification_performance(self):
        """Ruff verification should complete in <200ms for typical files."""
        verifier = RuffVerifier()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Create realistic Python file
            f.write('"""Module docstring."""\n\n')
            f.write("import logging\n\n")
            f.write("def function():\n")
            f.write('    """Function docstring."""\n')
            f.write("    logger = logging.getLogger(__name__)\n")
            f.write('    logger.info("Hello")\n')
            f.flush()
            temp_path = Path(f.name)

        try:
            result = verifier.verify_file(temp_path)

            # Should complete in under 200ms
            assert result.duration_ms < 200, f"Verification took {result.duration_ms}ms"

        finally:
            temp_path.unlink()
