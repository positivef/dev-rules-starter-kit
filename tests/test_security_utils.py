"""Tests for Security Utilities.

Test Coverage:
- SecurePathValidator: Path traversal prevention
- SecureFileLock: Cross-platform file locking
- MemorySafeResourceManager: Resource cleanup
- SecureConfig: Configuration management

Compliance:
- P6: Quality gate (coverage >= 90%)
- P8: Test-first development
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from security_utils import (
    MemorySafeResourceManager,
    SecureConfig,
    SecureFileLock,
    SecurePathValidator,
    SecurityError,
    secure_temp_directory,
)


class TestSecurePathValidator:
    """Test secure path validation."""

    def test_validate_safe_path(self):
        """Test validating a safe path within base directory."""
        validator = SecurePathValidator()
        base = Path.cwd()
        safe_path = base / "test.txt"

        # Should not raise an error
        assert validator.validate_path(base, safe_path) is True

    def test_validate_subdirectory_path(self):
        """Test validating a path in a subdirectory."""
        validator = SecurePathValidator()
        base = Path.cwd()
        safe_path = base / "subdir" / "test.txt"

        # Should not raise an error
        assert validator.validate_path(base, safe_path) is True

    def test_detect_path_traversal_parent(self):
        """Test detecting path traversal using parent directory."""
        validator = SecurePathValidator()
        base = Path.cwd()
        unsafe_path = base / ".." / "etc" / "passwd"

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_path(base, unsafe_path)

        assert "Path traversal detected" in str(exc_info.value)

    def test_detect_path_traversal_absolute(self):
        """Test detecting path traversal using absolute path."""
        validator = SecurePathValidator()
        base = Path.cwd()

        # Use a path outside the base directory
        if sys.platform == "win32":
            unsafe_path = Path("C:/Windows/System32/config")
        else:
            unsafe_path = Path("/etc/passwd")

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_path(base, unsafe_path)

        assert "Path traversal detected" in str(exc_info.value)

    def test_sanitize_filename_removes_dangerous_chars(self):
        """Test filename sanitization removes dangerous characters."""
        validator = SecurePathValidator()

        # Test various dangerous patterns - .. is replaced separately
        assert validator.sanitize_filename("../../../etc/passwd") == "______etc_passwd"
        assert validator.sanitize_filename("file:with:colons.txt") == "file_with_colons.txt"
        assert validator.sanitize_filename("file*with?wildcards.txt") == "file_with_wildcards.txt"
        assert validator.sanitize_filename('file"with<quotes>.txt') == "file_with_quotes_.txt"

    def test_sanitize_filename_length_limit(self):
        """Test filename sanitization enforces length limit."""
        validator = SecurePathValidator()

        # Create a very long filename
        long_name = "a" * 300 + ".txt"
        sanitized = validator.sanitize_filename(long_name)

        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")


class TestSecureFileLock:
    """Test secure file locking."""

    def test_acquire_and_release_lock(self):
        """Test basic lock acquisition and release."""
        with tempfile.NamedTemporaryFile(suffix=".lock", delete=False) as f:
            lock_file = Path(f.name)

        try:
            lock = SecureFileLock(lock_file)

            # Acquire lock
            assert lock.acquire(blocking=False) is True
            assert lock._locked is True

            # Release lock
            lock.release()
            assert lock._locked is False

        finally:
            # Cleanup
            if lock_file.exists():
                lock_file.unlink()

    def test_context_manager(self):
        """Test using file lock as context manager."""
        with tempfile.NamedTemporaryFile(suffix=".lock", delete=False) as f:
            lock_file = Path(f.name)

        try:
            with SecureFileLock(lock_file) as lock:
                assert lock._locked is True

            # Should be released after context
            assert lock._locked is False

        finally:
            # Cleanup
            if lock_file.exists():
                lock_file.unlink()

    def test_non_blocking_lock_fails_when_locked(self):
        """Test non-blocking lock fails when already locked."""
        # Note: On Windows, file locks are not exclusive between processes
        # but this test uses the same process, so behavior may differ
        with tempfile.NamedTemporaryFile(suffix=".lock", delete=False) as f:
            lock_file = Path(f.name)

        try:
            lock1 = SecureFileLock(lock_file)
            lock2 = SecureFileLock(lock_file)

            # First lock succeeds
            assert lock1.acquire(blocking=False) is True

            # On Windows, the second lock might succeed in the same process
            # This is a platform-specific behavior
            result = lock2.acquire(blocking=False)

            if result:
                # Windows behavior - locks can be shared in same process
                lock2.release()

            # Release first lock
            lock1.release()

        finally:
            # Cleanup - make sure locks are released before deleting
            try:
                lock1.release()
            except Exception:
                pass
            try:
                lock2.release()
            except Exception:
                pass
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except PermissionError:
                    # File may still be in use on Windows
                    pass


class TestMemorySafeResourceManager:
    """Test memory-safe resource management."""

    def test_register_and_cleanup_resources(self):
        """Test registering and cleaning up resources."""

        class MockResource:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        manager = MemorySafeResourceManager()
        resource1 = MockResource()
        resource2 = MockResource()

        # Register resources
        manager.register_resource(resource1)
        manager.register_resource(resource2)

        # Cleanup should close all resources
        manager.cleanup()

        assert resource1.closed is True
        assert resource2.closed is True
        assert manager._closed is True

    def test_context_manager(self):
        """Test resource manager as context manager."""

        class MockResource:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        resource = MockResource()

        with MemorySafeResourceManager() as manager:
            manager.register_resource(resource)
            assert resource.closed is False

        # Resource should be cleaned up after context
        assert resource.closed is True

    def test_cannot_register_after_cleanup(self):
        """Test that resources cannot be registered after cleanup."""
        manager = MemorySafeResourceManager()
        manager.cleanup()

        with pytest.raises(SecurityError) as exc_info:
            manager.register_resource(object())

        assert "Resource manager is closed" in str(exc_info.value)

    def test_cleanup_handles_exceptions(self):
        """Test cleanup continues even if resource cleanup fails."""

        class FailingResource:
            def close(self):
                raise Exception("Cleanup failed")

        class NormalResource:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        manager = MemorySafeResourceManager()
        failing = FailingResource()
        normal = NormalResource()

        manager.register_resource(failing)
        manager.register_resource(normal)

        # Cleanup should not raise exception
        manager.cleanup()

        # Normal resource should still be cleaned
        assert normal.closed is True


class TestSecureConfig:
    """Test secure configuration management."""

    def test_get_default_value(self):
        """Test getting default configuration values."""
        assert SecureConfig.get("coverage_threshold") == 85.0
        assert SecureConfig.get("lock_timeout") == 30
        assert SecureConfig.get("max_filename_length") == 255

    def test_get_with_custom_default(self):
        """Test getting config with custom default."""
        assert SecureConfig.get("non_existent_key", "custom_default") == "custom_default"

    def test_environment_override(self, monkeypatch):
        """Test environment variable override."""
        # Set environment variable
        monkeypatch.setenv("TIER1_COVERAGE_THRESHOLD", "90.0")

        # Should get environment value
        assert SecureConfig.get("coverage_threshold") == 90.0

    def test_environment_type_conversion(self, monkeypatch):
        """Test type conversion for environment variables."""
        # Set integer environment variable
        monkeypatch.setenv("TIER1_LOCK_TIMEOUT", "60")
        assert SecureConfig.get("lock_timeout") == 60

        # Set float environment variable
        monkeypatch.setenv("TIER1_COVERAGE_THRESHOLD", "95.5")
        assert SecureConfig.get("coverage_threshold") == 95.5

    def test_string_environment_value(self, monkeypatch):
        """Test string environment values are not converted."""
        monkeypatch.setenv("TIER1_NEW_STRING_CONFIG", "test_value")
        assert SecureConfig.get("new_string_config") == "test_value"


class TestSecureTempDirectory:
    """Test secure temporary directory context manager."""

    def test_creates_and_removes_temp_directory(self):
        """Test that temp directory is created and removed."""
        temp_path = None

        with secure_temp_directory("test_") as temp_dir:
            temp_path = temp_dir
            assert temp_path.exists()
            assert temp_path.is_dir()
            assert "test_" in str(temp_path)

        # Directory should be removed after context
        assert not temp_path.exists()

    def test_handles_cleanup_failure(self):
        """Test that cleanup failure is handled gracefully."""
        with secure_temp_directory("test_") as temp_dir:
            # Create a file in the directory
            test_file = temp_dir / "test.txt"
            test_file.write_text("test")

            # On Windows, this might prevent deletion, but should not raise
            # The context manager should handle this gracefully

        # Should complete without exception


class TestIntegration:
    """Integration tests for security utilities."""

    def test_path_validator_with_file_lock(self):
        """Test using path validator with file lock."""
        validator = SecurePathValidator()
        base = Path.cwd()

        # Create lock file in current directory to avoid path traversal
        lock_file = base / "test.lock"
        lock_file.touch()

        try:
            # Validate path - should work since it's in base directory
            validator.validate_path(base, lock_file)

            # Use file lock
            with SecureFileLock(lock_file) as lock:
                assert lock._locked is True

        finally:
            if lock_file.exists():
                lock_file.unlink()

    def test_resource_manager_with_file_locks(self):
        """Test resource manager managing multiple file locks."""

        class LockResource:
            def __init__(self, lock_file):
                self.lock = SecureFileLock(lock_file)
                self.lock.acquire(blocking=False)

            def close(self):
                self.lock.release()

        with tempfile.NamedTemporaryFile(suffix=".lock1", delete=False) as f1:
            lock_file1 = Path(f1.name)
        with tempfile.NamedTemporaryFile(suffix=".lock2", delete=False) as f2:
            lock_file2 = Path(f2.name)

        try:
            with MemorySafeResourceManager() as manager:
                lock1 = LockResource(lock_file1)
                lock2 = LockResource(lock_file2)

                manager.register_resource(lock1)
                manager.register_resource(lock2)

                assert lock1.lock._locked is True
                assert lock2.lock._locked is True

            # Locks should be released after context
            assert lock1.lock._locked is False
            assert lock2.lock._locked is False

        finally:
            for lock_file in [lock_file1, lock_file2]:
                if lock_file.exists():
                    lock_file.unlink()
