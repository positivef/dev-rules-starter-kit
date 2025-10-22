"""Integration Tests for Phase C Components

Tests the integration of CriticalFileDetector and VerificationCache
into the Development Assistant (Phase A).

Test Coverage:
1. Cache miss → verification → cache hit on second save
2. File modified (hash changed) → cache miss → new verification
3. Critical file detected → logs criticality score
4. Skip file (.md) → no verification attempted
5. Test file → always fast mode
6. Cache disabled via CLI → no caching happens
7. Clear cache flag → cache emptied
8. Evidence includes Phase C fields (from_cache, criticality_score, analysis_mode)

Performance Requirements:
- Cache lookup overhead: <2ms additional latency
- Total fast mode (with cache miss): <250ms
- Cache hit path: <50ms total
"""

import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Import Phase A components
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dev_assistant import (
    AssistantConfig,
    EvidenceLogger,
    FileChangeProcessor,
    RuffVerifier,
    VerificationResult,
)

# Import Phase C components
from critical_file_detector import AnalysisMode, CriticalFileDetector
from verification_cache import VerificationCache


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_python_file(temp_project_dir):
    """Create a sample Python file for testing"""
    file_path = temp_project_dir / "sample.py"
    file_path.write_text(
        '''"""Sample module for testing"""

def hello(name: str) -> str:
    """Return greeting message"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
'''
    )
    return file_path


@pytest.fixture
def critical_python_file(temp_project_dir):
    """Create a critical Python file (executor pattern)"""
    file_path = temp_project_dir / "task_executor.py"
    file_path.write_text(
        '''"""Task executor module"""

from constitutional_validator import validate

def execute_task(task):
    """Execute task with validation"""
    validate(task)
    return task.run()
'''
    )
    return file_path


@pytest.fixture
def test_file(temp_project_dir):
    """Create a test file"""
    test_dir = temp_project_dir / "tests"
    test_dir.mkdir(exist_ok=True)
    file_path = test_dir / "test_sample.py"
    file_path.write_text(
        '''"""Test module"""

def test_hello():
    """Test hello function"""
    assert True
'''
    )
    return file_path


@pytest.fixture
def markdown_file(temp_project_dir):
    """Create a markdown file"""
    file_path = temp_project_dir / "README.md"
    file_path.write_text("# Sample Project\n\nThis is a test.")
    return file_path


@pytest.fixture
def phase_c_config(temp_project_dir):
    """Create AssistantConfig with Phase C enabled"""
    return AssistantConfig(
        enabled=True,
        watch_paths=["scripts", "tests"],
        debounce_ms=500,
        verification_timeout_sec=2.0,
        log_retention_days=7,
        enable_ruff=True,
        enable_evidence=True,
        # Phase C configuration
        cache_enabled=True,
        cache_ttl_seconds=300,
        cache_max_entries=1000,
        criticality_threshold=0.5,
        critical_patterns=["*_executor.py", "*_validator.py", "constitutional_*.py"],
    )


@pytest.fixture
def detector():
    """Create CriticalFileDetector instance"""
    return CriticalFileDetector(git_enabled=False)  # Disable git for testing


@pytest.fixture
def cache(temp_project_dir):
    """Create VerificationCache instance"""
    cache_dir = temp_project_dir / ".cache"
    return VerificationCache(cache_dir=cache_dir, ttl_seconds=300, max_entries=1000)


@pytest.fixture
def mock_verifier():
    """Create mock RuffVerifier that returns success"""
    verifier = MagicMock(spec=RuffVerifier)
    verifier.verify_file.return_value = VerificationResult(
        file_path=Path("sample.py"),
        passed=True,
        violations=[],
        duration_ms=50.0,
        error=None,
    )
    return verifier


class TestPhaseACacheIntegration:
    """Test 1: Cache miss → verification → cache hit on second save"""

    def test_cache_miss_then_hit(self, sample_python_file, cache, mock_verifier):
        """Verify cache miss on first access, hit on second"""
        # First access: Cache miss
        cached_result = cache.get(sample_python_file)
        assert cached_result is None, "Expected cache miss on first access"

        # Run verification (fix: set correct file_path in result)
        mock_verifier.verify_file.return_value = VerificationResult(
            file_path=sample_python_file,  # Use actual file path
            passed=True,
            violations=[],
            duration_ms=50.0,
            error=None,
        )
        result = mock_verifier.verify_file(sample_python_file)
        assert result.passed is True

        # Store in cache
        cache.put(sample_python_file, result, mode="fast")

        # Second access: Cache hit
        cached_result = cache.get(sample_python_file)
        assert cached_result is not None, "Expected cache hit on second access"
        assert cached_result.passed is True
        assert str(cached_result.file_path) == str(sample_python_file)

    def test_cache_performance(self, sample_python_file, cache, mock_verifier):
        """Verify cache hit is significantly faster than verification"""
        # Prime cache
        mock_verifier.verify_file.return_value = VerificationResult(
            file_path=sample_python_file,
            passed=True,
            violations=[],
            duration_ms=50.0,
            error=None,
        )
        result = mock_verifier.verify_file(sample_python_file)
        cache.put(sample_python_file, result, mode="fast")

        # Measure cache hit time (average of 3 runs for stability)
        durations = []
        for _ in range(3):
            start = time.perf_counter()
            cached_result = cache.get(sample_python_file)
            cache_duration_ms = (time.perf_counter() - start) * 1000
            durations.append(cache_duration_ms)

        avg_duration_ms = sum(durations) / len(durations)

        assert cached_result is not None
        assert avg_duration_ms < 3.0, f"Cache lookup took {avg_duration_ms:.2f}ms average (expected <3ms for reliability)"


class TestPhaseAHashDetection:
    """Test 2: File modified (hash changed) → cache miss → new verification"""

    def test_file_modification_invalidates_cache(self, sample_python_file, cache, mock_verifier):
        """Verify cache invalidation when file content changes"""
        # Initial verification and cache
        result1 = mock_verifier.verify_file(sample_python_file)
        cache.put(sample_python_file, result1, mode="fast")

        # Verify cache hit
        cached = cache.get(sample_python_file)
        assert cached is not None, "Expected cache hit before modification"

        # Modify file (change content)
        sample_python_file.write_text(sample_python_file.read_text() + "\n# Modified comment\n")

        # Verify cache miss after modification
        cached_after = cache.get(sample_python_file)
        assert cached_after is None, "Expected cache miss after file modification"


class TestPhaseACriticalFileDetection:
    """Test 3: Critical file detected → logs criticality score"""

    def test_critical_file_classification(self, critical_python_file, detector):
        """Verify critical file is detected and scored correctly"""
        classification = detector.classify(critical_python_file)

        assert classification.mode == AnalysisMode.DEEP_MODE, (
            f"Expected DEEP_MODE for {critical_python_file.name}, " f"got {classification.mode.value}"
        )
        assert classification.criticality_score >= 0.5, f"Expected score >= 0.5, got {classification.criticality_score:.2f}"
        assert classification.pattern_score > 0, "Expected pattern match score"

    def test_evidence_includes_criticality(self, temp_project_dir, critical_python_file, mock_verifier):
        """Verify evidence logging includes Phase C fields"""
        evidence_logger = EvidenceLogger(runs_dir=temp_project_dir / "RUNS")
        detector = CriticalFileDetector(git_enabled=False)

        # Classify file
        classification = detector.classify(critical_python_file)

        # Run verification
        result = mock_verifier.verify_file(critical_python_file)

        # Log with Phase C metadata
        evidence_logger.log_verification(
            event_type="modified",
            file_path=critical_python_file,
            result=result,
            from_cache=False,
            criticality_score=classification.criticality_score,
            analysis_mode=classification.mode.value,
        )

        # Verify evidence contains Phase C fields
        events = evidence_logger._events
        assert len(events) == 1, "Expected one evidence event"

        event = events[0]
        assert "from_cache" in event, "Missing from_cache field"
        assert event["from_cache"] is False
        assert "criticality_score" in event, "Missing criticality_score field"
        assert event["criticality_score"] >= 0.5
        assert "analysis_mode" in event, "Missing analysis_mode field"
        assert event["analysis_mode"] == "deep"


class TestPhaseASkipFiles:
    """Test 4: Skip file (.md) → no verification attempted"""

    def test_markdown_file_skipped(self, markdown_file, detector):
        """Verify markdown files are classified as SKIP"""
        classification = detector.classify(markdown_file)

        assert (
            classification.mode == AnalysisMode.SKIP
        ), f"Expected SKIP for {markdown_file.name}, got {classification.mode.value}"
        assert "Non-code file" in classification.reason


class TestPhaseATestFiles:
    """Test 5: Test file → always fast mode"""

    def test_test_file_fast_mode(self, test_file, detector):
        """Verify test files always use FAST_MODE"""
        classification = detector.classify(test_file)

        assert (
            classification.mode == AnalysisMode.FAST_MODE
        ), f"Expected FAST_MODE for test file, got {classification.mode.value}"
        assert "Test file" in classification.reason


class TestPhaseACacheDisabled:
    """Test 6: Cache disabled via CLI → no caching happens"""

    def test_cache_disabled_config(self):
        """Verify cache can be disabled via configuration"""
        config = AssistantConfig(
            cache_enabled=False,
            enable_ruff=True,
        )

        assert config.cache_enabled is False
        errors = config.validate()
        assert len(errors) == 0, f"Configuration validation failed: {errors}"

    def test_processor_without_cache(self, sample_python_file, mock_verifier, temp_project_dir):
        """Verify FileChangeProcessor works without cache"""
        from queue import Queue
        from threading import Event
        import logging

        logger = logging.getLogger("test")
        event_queue = Queue()
        stop_event = Event()

        # Create processor without cache
        processor = FileChangeProcessor(
            event_queue=event_queue,
            stop_event=stop_event,
            logger=logger,
            ruff_verifier=mock_verifier,
            evidence_logger=None,
            detector=None,
            cache=None,  # No cache
        )

        # Process file change
        processor._process_change("modified", sample_python_file)

        # Verify verification was called
        mock_verifier.verify_file.assert_called_once()


class TestPhaseAClearCache:
    """Test 7: Clear cache flag → cache emptied"""

    def test_clear_cache_operation(self, cache, sample_python_file, mock_verifier):
        """Verify cache can be cleared"""
        # Add entry to cache
        result = mock_verifier.verify_file(sample_python_file)
        cache.put(sample_python_file, result, mode="fast")

        assert cache.size() == 1, "Expected cache to have 1 entry"

        # Clear cache
        cache.clear()

        assert cache.size() == 0, "Expected cache to be empty after clear"

        # Verify cache miss
        cached = cache.get(sample_python_file)
        assert cached is None, "Expected cache miss after clear"


class TestPhaseAEvidenceFields:
    """Test 8: Evidence includes Phase C fields"""

    def test_evidence_schema_with_phase_c(self, temp_project_dir, sample_python_file, mock_verifier):
        """Verify evidence logging includes all Phase C fields"""
        evidence_logger = EvidenceLogger(runs_dir=temp_project_dir / "RUNS")

        result = mock_verifier.verify_file(sample_python_file)

        # Log with all Phase C fields
        evidence_logger.log_verification(
            event_type="modified",
            file_path=sample_python_file,
            result=result,
            from_cache=True,
            criticality_score=0.6,
            analysis_mode="deep",
        )

        # Verify evidence structure
        events = evidence_logger._events
        assert len(events) == 1

        event = events[0]
        required_phase_a_fields = ["timestamp", "event_type", "file", "verification", "duration_ms"]
        required_phase_c_fields = ["from_cache", "criticality_score", "analysis_mode"]

        for field in required_phase_a_fields:
            assert field in event, f"Missing Phase A field: {field}"

        for field in required_phase_c_fields:
            assert field in event, f"Missing Phase C field: {field}"

        # Verify field values
        assert event["from_cache"] is True
        assert event["criticality_score"] == 0.6
        assert event["analysis_mode"] == "deep"

    def test_evidence_optional_phase_c_fields(self, temp_project_dir, sample_python_file, mock_verifier):
        """Verify evidence logging works without optional Phase C fields"""
        evidence_logger = EvidenceLogger(runs_dir=temp_project_dir / "RUNS")

        result = mock_verifier.verify_file(sample_python_file)

        # Log without optional fields (should not fail)
        evidence_logger.log_verification(
            event_type="modified",
            file_path=sample_python_file,
            result=result,
            from_cache=False,
            # No criticality_score or analysis_mode
        )

        events = evidence_logger._events
        assert len(events) == 1

        event = events[0]
        assert event["from_cache"] is False
        # Optional fields should not be present
        assert "criticality_score" not in event or event.get("criticality_score") is None
        assert "analysis_mode" not in event or event.get("analysis_mode") is None


class TestPhaseAEndToEndIntegration:
    """End-to-end integration tests"""

    def test_full_phase_c_workflow(
        self,
        temp_project_dir,
        critical_python_file,
        phase_c_config,
        mock_verifier,
    ):
        """Test complete Phase C workflow: classify → cache check → verify → cache store → evidence log"""
        from queue import Queue
        from threading import Event
        import logging

        # Setup components
        logger = logging.getLogger("test")
        event_queue = Queue()
        stop_event = Event()

        detector = CriticalFileDetector(git_enabled=False)
        cache_dir = temp_project_dir / ".cache"
        cache = VerificationCache(cache_dir=cache_dir)
        evidence_logger = EvidenceLogger(runs_dir=temp_project_dir / "RUNS")

        # Create processor with all Phase C components
        processor = FileChangeProcessor(
            event_queue=event_queue,
            stop_event=stop_event,
            logger=logger,
            ruff_verifier=mock_verifier,
            evidence_logger=evidence_logger,
            detector=detector,
            cache=cache,
        )

        # First processing: Cache miss
        processor._process_change("modified", critical_python_file)

        # Verify:
        # 1. Verification was called
        assert mock_verifier.verify_file.call_count == 1

        # 2. Result was cached
        assert cache.size() == 1

        # 3. Evidence was logged with Phase C fields
        events = evidence_logger._events
        assert len(events) == 1
        event = events[0]
        assert event["from_cache"] is False
        assert "criticality_score" in event
        assert event["criticality_score"] >= 0.5  # Critical file
        assert event["analysis_mode"] == "deep"

        # Second processing: Cache hit
        processor._process_change("modified", critical_python_file)

        # Verify:
        # 1. Verification was NOT called again (cache hit)
        assert mock_verifier.verify_file.call_count == 1  # Still 1

        # 2. Evidence was logged with from_cache=True
        assert len(evidence_logger._events) == 2
        second_event = evidence_logger._events[1]
        assert second_event["from_cache"] is True


class TestPhaseAPerformanceRequirements:
    """Performance requirement validation"""

    def test_cache_lookup_overhead(self, sample_python_file, cache, mock_verifier):
        """Verify cache lookup overhead is <2ms"""
        # Prime cache
        result = mock_verifier.verify_file(sample_python_file)
        cache.put(sample_python_file, result, mode="fast")

        # Measure cache lookup time (10 iterations for stability)
        durations = []
        for _ in range(10):
            start = time.perf_counter()
            _ = cache.get(sample_python_file)
            duration_ms = (time.perf_counter() - start) * 1000
            durations.append(duration_ms)

        avg_duration = sum(durations) / len(durations)
        assert avg_duration < 2.0, f"Cache lookup overhead too high: {avg_duration:.2f}ms (expected <2ms)"

    def test_cache_hit_path_performance(self, sample_python_file, cache, mock_verifier):
        """Verify total cache hit path is <50ms"""
        from queue import Queue
        from threading import Event
        import logging

        # Setup
        logger = logging.getLogger("test")
        event_queue = Queue()
        stop_event = Event()

        detector = CriticalFileDetector(git_enabled=False)

        processor = FileChangeProcessor(
            event_queue=event_queue,
            stop_event=stop_event,
            logger=logger,
            ruff_verifier=mock_verifier,
            evidence_logger=None,  # Skip evidence for pure cache performance
            detector=detector,
            cache=cache,
        )

        # Prime cache
        result = mock_verifier.verify_file(sample_python_file)
        cache.put(sample_python_file, result, mode="fast")

        # Measure full cache hit path
        start = time.perf_counter()
        processor._process_change("modified", sample_python_file)
        total_duration_ms = (time.perf_counter() - start) * 1000

        assert total_duration_ms < 50.0, f"Cache hit path too slow: {total_duration_ms:.2f}ms (expected <50ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
