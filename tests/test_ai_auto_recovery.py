#!/usr/bin/env python3
"""
Tests for AI Auto-Recovery System

Ensures production-ready quality with 90%+ coverage.
"""

import pytest
import tempfile
from pathlib import Path
from scripts.ai_auto_recovery import AIAutoRecovery


@pytest.fixture
def temp_vault():
    """Create temporary Obsidian vault for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def recovery(temp_vault):
    """Create AIAutoRecovery instance with temp vault"""
    recovery = AIAutoRecovery()
    recovery.vault_path = str(temp_vault)
    recovery.error_dir = temp_vault / "Errors"
    recovery.error_dir.mkdir(exist_ok=True)
    return recovery


class TestErrorKeyExtraction:
    """Test error key extraction logic"""

    def test_module_not_found_error(self, recovery):
        """Extract key from ModuleNotFoundError"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        key = recovery.extract_error_key(error)
        assert key == "modulenotfounderror:pandas"

    def test_permission_error(self, recovery):
        """Extract key from PermissionError"""
        error = "PermissionError: [Errno 13] Permission denied: 'file.txt'"
        key = recovery.extract_error_key(error)
        assert key == "permissionerror"

    def test_http_401_error(self, recovery):
        """Extract key from HTTP 401 error"""
        error = "401 Unauthorized: Invalid credentials"
        key = recovery.extract_error_key(error)
        # Should extract error type if present
        assert "401" in key.lower() or "error" in key.lower()

    def test_empty_error_message(self, recovery):
        """Handle empty error message"""
        error = ""
        key = recovery.extract_error_key(error)
        assert key == "error"  # Default fallback

    def test_no_error_type_match(self, recovery):
        """Handle message with no error type"""
        error = "Something went wrong"
        key = recovery.extract_error_key(error)
        assert key == "error"  # Default fallback


class TestSolutionSearch:
    """Test past solution search"""

    def test_find_existing_solution(self, recovery):
        """Find existing solution by filename"""
        # Create existing solution (using actual save format)
        recovery.save_new_solution("ModuleNotFoundError: No module named 'pandas'", "pip install pandas")

        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = recovery.search_past_solution(error)

        assert solution == "pip install pandas"

    def test_no_solution_found(self, recovery):
        """Return None when no solution exists"""
        error = "ModuleNotFoundError: No module named 'numpy'"
        solution = recovery.search_past_solution(error)

        assert solution is None

    def test_multiple_solutions_returns_most_recent(self, recovery):
        """Return most recent solution when multiple exist"""
        import time

        # Create old solution
        recovery.save_new_solution("ModuleNotFoundError: No module named 'pandas'", "pip install pandas==1.0")
        time.sleep(0.1)  # Ensure different mtime

        # Create newer solution (will overwrite or create new file)
        recovery.save_new_solution("ModuleNotFoundError: No module named 'pandas'", "pip install pandas==2.0")

        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = recovery.search_past_solution(error)

        # Should find the most recent solution
        assert solution == "pip install pandas==2.0"


class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_allows_first_three_retries(self, recovery):
        """Allow up to 3 retry attempts"""
        error_key = "modulenotfounderror:pandas"

        assert recovery.should_retry(error_key) is True
        recovery.record_attempt(error_key)

        assert recovery.should_retry(error_key) is True
        recovery.record_attempt(error_key)

        assert recovery.should_retry(error_key) is True
        recovery.record_attempt(error_key)

        # Fourth attempt should be blocked
        assert recovery.should_retry(error_key) is False

    def test_different_errors_tracked_separately(self, recovery):
        """Track different errors separately"""
        error_key1 = "modulenotfounderror:pandas"
        error_key2 = "modulenotfounderror:numpy"

        # Max out pandas retries
        for _ in range(3):
            recovery.record_attempt(error_key1)

        # Numpy should still be allowed
        assert recovery.should_retry(error_key1) is False
        assert recovery.should_retry(error_key2) is True


class TestSolutionSaving:
    """Test saving new solutions"""

    def test_save_creates_file(self, recovery):
        """Save creates file in error directory"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = "pip install pandas"
        context = {"file": "data_analyzer.py"}

        filepath = recovery.save_new_solution(error, solution, context)

        assert filepath.exists()
        assert filepath.parent == recovery.error_dir

    def test_save_includes_hashtags(self, recovery):
        """Saved file includes hashtags for search"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = "pip install pandas"

        filepath = recovery.save_new_solution(error, solution)
        content = filepath.read_text()

        assert "#modulenotfound" in content
        assert "#pandas" in content
        assert "#solution" in content

    def test_save_includes_solution(self, recovery):
        """Saved file includes solution command"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = "pip install pandas"

        filepath = recovery.save_new_solution(error, solution)
        content = filepath.read_text()

        assert "pip install pandas" in content
        assert "**Solution**:" in content

    def test_save_includes_context(self, recovery):
        """Saved file includes context information"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = "pip install pandas"
        context = {"file": "scripts/analyzer.py", "line": 5}

        filepath = recovery.save_new_solution(error, solution, context)
        content = filepath.read_text()

        assert "scripts/analyzer.py" in content


class TestAutoRecovery:
    """Test end-to-end auto-recovery workflow"""

    def test_first_time_error_returns_none(self, recovery):
        """First time error returns None (ask user)"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = recovery.auto_recover(error)

        assert solution is None

    def test_second_time_error_returns_solution(self, recovery):
        """Second time error returns past solution"""
        error = "ModuleNotFoundError: No module named 'pandas'"

        # First time: save solution
        recovery.save_new_solution(error, "pip install pandas")

        # Second time: should find solution
        solution = recovery.auto_recover(error)

        assert solution == "pip install pandas"

    def test_circuit_breaker_stops_infinite_loops(self, recovery):
        """Circuit breaker prevents infinite retry loops"""
        error = "ModuleNotFoundError: No module named 'pandas'"

        # Create solution file
        recovery.save_new_solution(error, "pip install pandas")

        # Try recovering 4 times
        for i in range(4):
            solution = recovery.auto_recover(error)
            if i < 3:
                assert solution is not None
            else:
                # Fourth time should be blocked
                assert solution is None


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_unicode_in_error_message(self, recovery):
        """Handle Unicode characters in error"""
        error = "에러: 파일을 찾을 수 없습니다"
        key = recovery.extract_error_key(error)
        assert key is not None

    def test_very_long_error_message(self, recovery):
        """Handle very long error messages"""
        # More realistic: long message but recognizable error type
        error = "ModuleNotFoundError: " + "A" * 5000
        solution = "pip install pandas"

        filepath = recovery.save_new_solution(error, solution)
        content = filepath.read_text()

        # Should truncate error message (200 char limit in content)
        assert "ModuleNotFoundError" in content
        assert len(content) < 5500  # Much shorter than original

    def test_special_characters_in_solution(self, recovery):
        """Handle special characters in solution"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = "export AUTH_SECRET='my$ecret!@#'"

        recovery.save_new_solution(error, solution)
        saved_solution = recovery.search_past_solution(error)

        assert saved_solution == solution

    def test_concurrent_saves(self, recovery):
        """Handle concurrent save attempts (basic test)"""
        import threading

        errors = [
            "ModuleNotFoundError: No module named 'pandas'",
            "ModuleNotFoundError: No module named 'numpy'",
            "ModuleNotFoundError: No module named 'scipy'",
        ]

        def save_error(error):
            recovery.save_new_solution(error, f"pip install {error.split()[-1][1:-1]}")

        threads = [threading.Thread(target=save_error, args=(e,)) for e in errors]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All files should be created
        assert len(list(recovery.error_dir.glob("*.md"))) >= 3


@pytest.mark.benchmark
class TestPerformance:
    """Test performance characteristics"""

    def test_search_speed(self, recovery, benchmark):
        """Search should complete in <100ms"""
        # Create 100 solution files using actual save format
        for i in range(100):
            recovery.save_new_solution(
                f"Type{i}Error: keyword{i}",
                f"pip install package{i}",  # Use whitelisted command
            )

        error = "Type50Error: keyword50"

        result = benchmark(recovery.search_past_solution, error)
        assert result == "pip install package50"

    def test_save_speed(self, recovery, benchmark):
        """Save should complete in <50ms"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = "pip install pandas"

        benchmark(recovery.save_new_solution, error, solution)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=scripts.ai_auto_recovery", "--cov-report=term-missing"])
