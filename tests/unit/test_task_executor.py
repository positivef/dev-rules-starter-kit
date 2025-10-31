"""
Unit tests for task_executor.py core functions
Dev Rules Starter Kit - Phase 4: Unit Test Framework

Target: Import-based testing for coverage measurement
Focus: Pure functions and isolated logic units
"""

import pytest
import json
import hashlib
from pathlib import Path

# Import functions from task_executor for unit testing
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from task_executor import (
    plan_hash,
    sha256_file,
    ports_free,
    build_env,
    _looks_like_file,
    atomic_write_json,
)


class TestPlanHash:
    """Test plan hash generation for contract verification"""

    def test_plan_hash_consistent_for_same_contract(self):
        """Same contract should always produce same hash"""
        contract = {"task_id": "TEST-001", "title": "Test Task", "commands": [{"exec": ["echo", "hello"]}]}

        hash1 = plan_hash(contract)
        hash2 = plan_hash(contract)

        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated to 16 chars for human approval

    def test_plan_hash_different_for_different_contracts(self):
        """Different contracts should produce different hashes"""
        # plan_hash only considers commands, gates, acceptance_criteria
        contract1 = {"commands": [{"exec": ["echo", "1"]}]}
        contract2 = {"commands": [{"exec": ["echo", "2"]}]}

        hash1 = plan_hash(contract1)
        hash2 = plan_hash(contract2)

        assert hash1 != hash2

    def test_plan_hash_ignores_key_order(self):
        """Hash should be same regardless of key order (canonical serialization)"""
        contract1 = {"commands": [{"a": 1}], "gates": [{"b": 2}]}
        contract2 = {"gates": [{"b": 2}], "commands": [{"a": 1}]}

        hash1 = plan_hash(contract1)
        hash2 = plan_hash(contract2)

        # Implementation uses sort_keys=True
        assert hash1 == hash2


class TestSHA256File:
    """Test file SHA-256 hashing"""

    def test_sha256_file_with_text_content(self, tmp_path):
        """Hash text file correctly"""
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"
        test_file.write_text(content, encoding="utf-8")

        file_hash = sha256_file(test_file)

        # Verify hash format
        assert len(file_hash) == 64
        assert all(c in "0123456789abcdef" for c in file_hash)

        # Verify hash is correct
        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert file_hash == expected_hash

    def test_sha256_file_empty_file(self, tmp_path):
        """Handle empty file correctly"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        file_hash = sha256_file(test_file)

        # Empty file has specific hash
        expected_hash = hashlib.sha256(b"").hexdigest()
        assert file_hash == expected_hash


class TestPortsFree:
    """Test port availability checking"""

    def test_ports_free_with_high_unlikely_ports(self):
        """High port numbers should typically be free (no exception)"""
        # Use very high port numbers unlikely to be in use
        ports = [54321, 54322, 54323]

        # If ports are free, function returns None (no exception raised)
        result = ports_free(ports)
        assert result is None

    def test_ports_free_with_empty_list(self):
        """Empty port list should not raise exception"""
        result = ports_free([])
        assert result is None

        result = ports_free(None)
        assert result is None


class TestBuildEnv:
    """Test environment variable building"""

    def test_build_env_includes_path(self):
        """Environment should include PATH"""
        env = build_env()

        assert "PATH" in env
        assert isinstance(env["PATH"], str)
        assert len(env["PATH"]) > 0

    def test_build_env_returns_dict(self):
        """Should return dictionary of strings"""
        env = build_env()

        assert isinstance(env, dict)
        assert all(isinstance(k, str) for k in env.keys())
        assert all(isinstance(v, str) for v in env.values())


class TestLooksLikeFile:
    """Test file path detection heuristic (detects glob patterns)"""

    def test_looks_like_file_without_glob_patterns(self):
        """Paths without glob patterns look like files"""
        assert _looks_like_file("config.yaml") is True
        assert _looks_like_file("script.py") is True
        assert _looks_like_file("data.json") is True
        assert _looks_like_file("/path/to/file.txt") is True
        assert _looks_like_file("README") is True  # No glob pattern = file
        assert _looks_like_file("scripts") is True  # No glob pattern = file

    def test_looks_like_file_with_glob_patterns(self):
        """Paths with glob patterns don't look like files"""
        assert _looks_like_file("*.py") is False  # Asterisk is glob
        assert _looks_like_file("test?.txt") is False  # Question mark is glob
        assert _looks_like_file("file[123].txt") is False  # Brackets are glob
        assert _looks_like_file("src/**/*.py") is False  # Multiple globs

    def test_looks_like_file_edge_cases(self):
        """Edge cases in file detection"""
        assert _looks_like_file("") is True  # Empty string, no glob pattern
        assert _looks_like_file(".") is True  # Current dir, no glob pattern
        assert _looks_like_file("..") is True  # Parent dir, no glob pattern


class TestAtomicWriteJSON:
    """Test atomic JSON writing"""

    def test_atomic_write_json_creates_file(self, tmp_path):
        """Should create JSON file atomically"""
        target_file = tmp_path / "test.json"
        data = {"key": "value", "number": 42}

        atomic_write_json(target_file, data)

        assert target_file.exists()

        # Verify content
        with open(target_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == data

    def test_atomic_write_json_overwrites_existing(self, tmp_path):
        """Should overwrite existing file atomically"""
        target_file = tmp_path / "test.json"

        # Write initial data
        initial_data = {"old": "data"}
        target_file.write_text(json.dumps(initial_data), encoding="utf-8")

        # Overwrite atomically
        new_data = {"new": "data", "number": 123}
        atomic_write_json(target_file, new_data)

        # Verify new content
        with open(target_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == new_data
        assert "old" not in loaded

    def test_atomic_write_json_preserves_unicode(self, tmp_path):
        """Should handle Unicode content correctly"""
        target_file = tmp_path / "unicode.json"
        data = {"korean": "한글", "japanese": "日本語", "emoji": "🚀"}

        atomic_write_json(target_file, data)

        with open(target_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == data
        assert loaded["korean"] == "한글"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
