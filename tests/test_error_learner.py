"""
Unit tests for Error Learning Database
Target coverage: ≥ 90%
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from error_learner import ErrorLearner, capture_error_quick


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing"""
    db_path = tmp_path / "test_errors.json"
    return str(db_path)


@pytest.fixture
def learner(temp_db):
    """ErrorLearner instance with temp database"""
    return ErrorLearner(db_path=temp_db)


class TestErrorCapture:
    """Test error capture functionality"""

    def test_capture_basic_error(self, learner):
        """Test basic error capture"""
        error_id = learner.capture_error(
            error_type="ModuleNotFoundError",
            error_msg="No module named 'pydantic_settings'",
            context="app/config.py:10",
            solution="pip install pydantic-settings",
            tags=["dependency", "import"],
        )

        assert error_id is not None
        assert len(error_id) == 8  # SHA-256[:8]
        assert error_id in learner.errors
        assert learner.errors[error_id]["occurrences"] == 1

    def test_capture_duplicate_error(self, learner):
        """Test duplicate error increments occurrence count"""
        error_id1 = learner.capture_error(
            "TypeError",
            "int() argument must be a string",
            "test.py:1",
            "Check input type",
        )

        error_id2 = learner.capture_error(
            "TypeError",
            "int() argument must be a string",
            "test.py:5",
            "Check input type",
        )

        assert error_id1 == error_id2
        assert learner.errors[error_id1]["occurrences"] == 2
        assert len(learner.errors[error_id1]["contexts"]) == 2

    def test_capture_with_tags(self, learner):
        """Test error capture with tags"""
        error_id = learner.capture_error(
            "SecurityError",
            "eval() is dangerous",
            "bad.py:10",
            "Use ast.literal_eval()",
            tags=["eval", "security", "injection"],
        )

        assert "eval" in learner.errors[error_id]["tags"]
        assert "security" in learner.errors[error_id]["tags"]

    def test_capture_without_tags(self, learner):
        """Test error capture without tags"""
        error_id = learner.capture_error(
            "ValueError", "Invalid value", "test.py:1", "Validate input"
        )

        assert learner.errors[error_id]["tags"] == []


class TestErrorSearch:
    """Test error search functionality"""

    def test_check_known_errors_exact_match(self, learner):
        """Test exact match for known errors"""
        learner.capture_error(
            "ModuleNotFoundError",
            "No module named 'foo'",
            "test.py:1",
            "pip install foo",
        )

        result = learner.check_known_errors("No module named 'foo'")

        assert result is not None
        assert result["solution"] == "pip install foo"
        assert result["type"] == "ModuleNotFoundError"

    def test_check_known_errors_normalized_match(self, learner):
        """Test normalized pattern matching"""
        learner.capture_error(
            "ModuleNotFoundError",
            "No module named 'foo'",
            "test.py:1",
            "pip install foo",
        )

        # Different module name should still match pattern
        result = learner.check_known_errors("No module named 'bar'")

        assert result is not None
        assert result["solution"] == "pip install foo"

    def test_check_known_errors_fuzzy_match(self, learner):
        """Test fuzzy substring matching"""
        learner.capture_error(
            "FileNotFoundError",
            "File '/path/to/config.json' not found in directory",
            "app/main.py:20",
            "Create config file",
        )

        # Shorter message should trigger fuzzy substring match
        result = learner.check_known_errors("File '/other/path.json' not found")

        assert result is not None
        assert result["match_type"] == "fuzzy"

    def test_check_unknown_error(self, learner):
        """Test search for unknown error"""
        result = learner.check_known_errors("Some completely new error")

        assert result is None


class TestRegressionPrevention:
    """Test regression prevention warnings"""

    def test_prevent_regression_detects_risky_pattern(self, learner):
        """Test detection of risky code patterns"""
        learner.capture_error(
            "SecurityError",
            "eval() is dangerous",
            "bad.py:10",
            "Use ast.literal_eval()",
            tags=["eval", "security"],
        )

        warnings = learner.prevent_regression("x = eval(user_input)")

        assert len(warnings) > 0
        assert warnings[0]["pattern"] == "eval"
        assert warnings[0]["severity"] in ["high", "medium"]

    def test_prevent_regression_multiple_patterns(self, learner):
        """Test detection of multiple risky patterns"""
        learner.capture_error(
            "Error1", "Error with eval", "test.py:1", "Fix1", tags=["eval"]
        )

        learner.capture_error(
            "Error2", "Error with exec", "test.py:2", "Fix2", tags=["exec"]
        )

        warnings = learner.prevent_regression("eval(x); exec(y)")

        assert len(warnings) == 2

    def test_prevent_regression_no_warnings(self, learner):
        """Test clean code generates no warnings"""
        learner.capture_error(
            "Error", "Error", "test.py:1", "Fix", tags=["dangerous_function"]
        )

        warnings = learner.prevent_regression("safe_code = 123")

        assert len(warnings) == 0


class TestPersistence:
    """Test database persistence"""

    def test_save_and_load(self, temp_db):
        """Test saving and loading database"""
        learner1 = ErrorLearner(db_path=temp_db)
        error_id = learner1.capture_error(
            "TestError", "Test message", "test.py:1", "Test solution"
        )

        # Create new instance (should load from disk)
        learner2 = ErrorLearner(db_path=temp_db)

        assert error_id in learner2.errors
        assert learner2.errors[error_id]["type"] == "TestError"

    def test_corrupted_db_recovery(self, temp_db):
        """Test recovery from corrupted database"""
        # Create corrupted JSON file
        Path(temp_db).write_text("{ invalid json", encoding="utf-8")

        # Should recover gracefully
        learner = ErrorLearner(db_path=temp_db)

        assert learner.errors == {}


class TestStatistics:
    """Test statistics generation"""

    def test_get_stats_empty_db(self, learner):
        """Test stats for empty database"""
        stats = learner.get_stats()

        assert stats["total_unique_errors"] == 0
        assert stats["total_occurrences"] == 0
        assert len(stats["most_common"]) == 0

    def test_get_stats_with_errors(self, learner):
        """Test stats calculation"""
        # Add multiple errors with different occurrence counts
        learner.capture_error("Error1", "msg1", "ctx1", "sol1")
        learner.capture_error("Error1", "msg1", "ctx1", "sol1")  # 2 occurrences
        learner.capture_error("Error2", "msg2", "ctx2", "sol2")  # 1 occurrence

        stats = learner.get_stats()

        assert stats["total_unique_errors"] == 2
        assert stats["total_occurrences"] == 3
        assert len(stats["most_common"]) == 2
        # Most common should be first
        assert stats["most_common"][0]["occurrences"] == 2


class TestObsidianIntegration:
    """Test Obsidian MOC generation"""

    def test_generate_obsidian_moc(self, learner):
        """Test Obsidian MOC generation"""
        learner.capture_error(
            "TestError",
            "Test message",
            "test.py:1",
            "Test solution",
            tags=["test", "demo"],
        )

        moc = learner.generate_obsidian_moc()

        assert "Error Learning Database - MOC" in moc
        assert "TestError" in moc
        assert "Test solution" in moc
        assert "#test" in moc

    def test_export_to_obsidian(self, learner, tmp_path):
        """Test exporting to Obsidian vault"""
        learner.capture_error("Error", "Message", "ctx", "Solution")

        vault_path = tmp_path / "obsidian_vault"
        vault_path.mkdir()

        learner.export_to_obsidian(str(vault_path))

        moc_file = vault_path / "Error_Learning_Database.md"
        assert moc_file.exists()

        content = moc_file.read_text(encoding="utf-8")
        assert "Error Learning Database - MOC" in content


class TestQuickCapture:
    """Test convenience function"""

    def test_capture_error_quick(self, temp_db, monkeypatch):
        """Test quick error capture function"""
        # Mock ErrorLearner to use temp_db
        monkeypatch.setattr(
            "error_learner.ErrorLearner", lambda: ErrorLearner(db_path=temp_db)
        )

        try:
            raise ValueError("Test error")
        except ValueError as e:
            capture_error_quick(e, "test.py:1", "Fix it")

        # Verify error was captured
        learner = ErrorLearner(db_path=temp_db)
        result = learner.check_known_errors("Test error")

        assert result is not None
        assert result["type"] == "ValueError"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_error_message(self, learner):
        """Test handling of empty error message"""
        error_id = learner.capture_error("Error", "", "ctx", "sol")

        assert error_id is not None

    def test_very_long_error_message(self, learner):
        """Test handling of very long error message"""
        long_msg = "A" * 10000
        error_id = learner.capture_error("Error", long_msg, "ctx", "sol")

        assert error_id is not None
        assert learner.errors[error_id]["message"] == long_msg

    def test_special_characters_in_message(self, learner):
        """Test special characters handling"""
        error_id = learner.capture_error(
            "Error",
            "Error with 'quotes' and \"double quotes\" and \n newlines",
            "ctx",
            "sol",
        )

        assert error_id is not None

    def test_unicode_in_message(self, learner):
        """Test Unicode characters"""
        error_id = learner.capture_error(
            "한글Error", "에러 메시지 with emoji 🔥", "test.py:1", "해결책"
        )

        assert error_id is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--cov=error_learner", "--cov-report=term-missing"])
