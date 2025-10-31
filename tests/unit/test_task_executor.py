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
    write_lessons_template,
    write_file,
    replace,
    detect_agent_id,
    collect_files_to_lock,
    acquire_lock,
    release_lock,
    write_prompt_feedback,
    ensure_secrets,
    run_shell_command,
    SecurityError,
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


class TestWriteLessonsTemplate:
    """Test lessons template file generation"""

    def test_write_lessons_template_creates_file(self, tmp_path):
        """Should create lessons.md with correct template"""
        contract = {"task_id": "TEST-001", "project": "TestProject"}

        write_lessons_template(tmp_path, contract, "completed")

        lessons_file = tmp_path / "lessons.md"
        assert lessons_file.exists()

        content = lessons_file.read_text(encoding="utf-8")
        assert "# Lessons Learned - TEST-001 (COMPLETED)" in content
        assert "#lesson #TestProject" in content
        assert "## Summary" in content
        assert "## What Worked" in content

    def test_write_lessons_template_with_error_message(self, tmp_path):
        """Should include error message in summary"""
        contract = {"task_id": "TEST-002"}
        error_msg = "Connection timeout"

        write_lessons_template(tmp_path, contract, "failed", error_msg)

        content = (tmp_path / "lessons.md").read_text(encoding="utf-8")
        assert "Failure reason: Connection timeout" in content

    def test_write_lessons_template_skips_if_exists(self, tmp_path):
        """Should not overwrite existing lessons.md"""
        lessons_file = tmp_path / "lessons.md"
        existing_content = "# Existing content"
        lessons_file.write_text(existing_content, encoding="utf-8")

        contract = {"task_id": "TEST-003"}
        write_lessons_template(tmp_path, contract, "completed")

        # Should not overwrite
        assert lessons_file.read_text(encoding="utf-8") == existing_content


class TestWriteFile:
    """Test write_file internal function"""

    def test_write_file_creates_new_file(self, tmp_path):
        """Should create new file with content"""
        target_file = tmp_path / "test.txt"
        content = "Hello, World!"

        result = write_file(str(target_file), content)

        assert target_file.exists()
        assert target_file.read_text(encoding="utf-8") == content
        assert result["status"] == "success"

    def test_write_file_overwrites_existing(self, tmp_path):
        """Should overwrite existing file"""
        target_file = tmp_path / "test.txt"
        target_file.write_text("Old content", encoding="utf-8")

        new_content = "New content"
        write_file(str(target_file), new_content)

        assert target_file.read_text(encoding="utf-8") == new_content


class TestReplace:
    """Test replace internal function"""

    def test_replace_simple_string(self, tmp_path):
        """Should replace string in file"""
        target_file = tmp_path / "test.txt"
        target_file.write_text("Hello, World!", encoding="utf-8")

        result = replace(str(target_file), "World", "Python")

        assert target_file.read_text(encoding="utf-8") == "Hello, Python!"
        assert result["status"] == "success"
        assert result["replacements"] == 1

    def test_replace_multiple_occurrences(self, tmp_path):
        """Should replace all occurrences"""
        target_file = tmp_path / "test.txt"
        target_file.write_text("foo bar foo baz foo", encoding="utf-8")

        replace(str(target_file), "foo", "qux")

        assert target_file.read_text(encoding="utf-8") == "qux bar qux baz qux"


class TestDetectAgentId:
    """Test agent ID detection"""

    def test_detect_agent_id_from_env(self, monkeypatch):
        """Should use AGENT_ID environment variable"""
        monkeypatch.setenv("AGENT_ID", "custom-agent")

        agent_id = detect_agent_id()

        assert agent_id == "custom-agent"

    def test_detect_agent_id_codex(self, monkeypatch):
        """Should detect Codex from environment"""
        monkeypatch.delenv("AGENT_ID", raising=False)
        monkeypatch.setenv("CODEX_CLI", "true")

        agent_id = detect_agent_id()

        assert agent_id == "codex"

    def test_detect_agent_id_claude(self, monkeypatch):
        """Should detect Claude from environment"""
        monkeypatch.delenv("AGENT_ID", raising=False)
        monkeypatch.delenv("CODEX_CLI", raising=False)
        monkeypatch.setenv("CLAUDE_CODE", "true")

        agent_id = detect_agent_id()

        assert agent_id == "claude"

    def test_detect_agent_id_fallback(self, monkeypatch):
        """Should generate UUID-based ID as fallback"""
        monkeypatch.delenv("AGENT_ID", raising=False)
        monkeypatch.delenv("CODEX_CLI", raising=False)
        monkeypatch.delenv("CLAUDE_CODE", raising=False)
        monkeypatch.delenv("GEMINI_AI", raising=False)

        agent_id = detect_agent_id()

        assert agent_id.startswith("agent-")
        assert len(agent_id) == 14  # "agent-" + 8 hex chars


class TestCollectFilesToLock:
    """Test file collection for locking"""

    def test_collect_files_from_evidence(self):
        """Should collect files from evidence list"""
        contract = {
            "evidence": ["file1.txt", "file2.py", "*.md"]  # Last is glob, excluded
        }

        files = collect_files_to_lock(contract)

        assert "file1.txt" in files
        assert "file2.py" in files
        assert "*.md" not in files  # Glob patterns excluded

    def test_collect_files_empty_contract(self):
        """Should handle empty contract"""
        files = collect_files_to_lock({})

        assert files == []


class TestAcquireLock:
    """Test lock acquisition"""

    def test_acquire_lock_creates_lock_file(self, tmp_path):
        """Should create lock file"""
        lock_path = acquire_lock("test-lock", tmp_path)

        assert lock_path.exists()
        assert lock_path.name == "test-lock.lock"

        # Cleanup
        release_lock(lock_path)

    def test_acquire_lock_stores_pid(self, tmp_path):
        """Should store process ID in lock file"""
        import os as os_module

        lock_path = acquire_lock("test-lock", tmp_path)

        pid_str = lock_path.read_text(encoding="utf-8")
        assert pid_str == str(os_module.getpid())

        # Cleanup
        release_lock(lock_path)


class TestReleaseLock:
    """Test lock release"""

    def test_release_lock_removes_file(self, tmp_path):
        """Should remove lock file"""
        lock_path = acquire_lock("test-lock", tmp_path)
        assert lock_path.exists()

        release_lock(lock_path)

        assert not lock_path.exists()

    def test_release_lock_nonexistent_file(self, tmp_path):
        """Should not raise error for nonexistent lock"""
        lock_path = tmp_path / "nonexistent.lock"

        # Should not raise exception
        release_lock(lock_path)


class TestWritePromptFeedback:
    """Test prompt feedback statistics writing"""

    def test_write_prompt_feedback_with_successes(self, tmp_path):
        """Should create feedback file with statistics"""
        stats = [
            {
                "command_id": "cmd1",
                "context": "test",
                "original_tokens": 100,
                "compressed_tokens": 60,
                "savings_pct": 40.0,
                "rules_applied": ["rule1"],
            },
            {
                "command_id": "cmd2",
                "original_tokens": 200,
                "compressed_tokens": 120,
                "savings_pct": 40.0,
            },
        ]

        write_prompt_feedback(tmp_path, stats)

        feedback_file = tmp_path / "prompt_feedback.json"
        assert feedback_file.exists()

        data = json.loads(feedback_file.read_text(encoding="utf-8"))
        assert data["entries"] == 2
        assert data["summary"]["total_prompts"] == 2
        assert data["summary"]["total_original_tokens"] == 300
        assert data["summary"]["total_compressed_tokens"] == 180
        assert data["summary"]["average_savings_pct"] == 40.0

    def test_write_prompt_feedback_with_errors(self, tmp_path):
        """Should include error information"""
        stats = [
            {"command_id": "cmd1", "original_tokens": 100},
            {"command_id": "cmd2", "error": "Timeout"},
        ]

        write_prompt_feedback(tmp_path, stats)

        data = json.loads((tmp_path / "prompt_feedback.json").read_text(encoding="utf-8"))
        assert "errors" in data
        assert len(data["errors"]) == 1
        assert data["errors"][0]["error"] == "Timeout"

    def test_write_prompt_feedback_empty_stats(self, tmp_path):
        """Should skip writing for empty stats"""
        write_prompt_feedback(tmp_path, [])

        feedback_file = tmp_path / "prompt_feedback.json"
        assert not feedback_file.exists()


class TestEnsureSecrets:
    """Test secret environment variable validation"""

    def test_ensure_secrets_all_present(self, monkeypatch):
        """Should pass when all secrets present"""
        monkeypatch.setenv("SECRET1", "value1")
        monkeypatch.setenv("SECRET2", "value2")

        # Should not raise exception
        ensure_secrets(["SECRET1", "SECRET2"], "test context")

    def test_ensure_secrets_missing_key(self, monkeypatch):
        """Should raise SecurityError for missing secret"""
        monkeypatch.delenv("MISSING_SECRET", raising=False)

        with pytest.raises(SecurityError) as exc_info:
            ensure_secrets(["MISSING_SECRET"], "test context")

        assert "Missing required secret: MISSING_SECRET" in str(exc_info.value)
        assert "test context" in str(exc_info.value)

    def test_ensure_secrets_empty_list(self):
        """Should pass for empty secret list"""
        # Should not raise exception
        ensure_secrets([], "test")
        ensure_secrets(None, "test")


class TestRunShellCommand:
    """Test shell command execution (dummy function)"""

    def test_run_shell_command_returns_success(self):
        """Should return success status"""
        result = run_shell_command("echo hello", "test command")

        assert result["status"] == "success"
        assert result["command"] == "echo hello"
        assert result["exit_code"] == 0
        assert "stdout" in result

    def test_run_shell_command_with_description(self):
        """Should handle description parameter"""
        description = "Testing shell command"
        result = run_shell_command("test", description)

        assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
