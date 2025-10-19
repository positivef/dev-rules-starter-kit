"""
Unit tests for Token Optimizer
Target coverage: >= 90%
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from token_optimizer import TokenOptimizer, compress_quick


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing"""
    db_path = tmp_path / "test_tokens.json"
    return str(db_path)


@pytest.fixture
def optimizer(temp_db):
    """TokenOptimizer instance with temp database"""
    return TokenOptimizer(db_path=temp_db, default_budget=100000)


class TestSessionManagement:
    """Test session lifecycle management"""

    def test_start_session_basic(self, optimizer):
        """Test starting a new session"""
        session_id = optimizer.start_session(
            "test_session",
            budget=50000,
            metadata={"project": "test"},
        )

        assert session_id is not None
        assert len(session_id) == 8  # SHA-256[:8]
        assert session_id in optimizer.sessions
        assert optimizer.sessions[session_id]["active"] is True
        assert optimizer.sessions[session_id]["budget"] == 50000

    def test_start_session_default_budget(self, optimizer):
        """Test session with default budget"""
        session_id = optimizer.start_session("default_budget_session")

        assert optimizer.sessions[session_id]["budget"] == 100000

    def test_end_session(self, optimizer):
        """Test ending a session"""
        session_id = optimizer.start_session("ending_session")

        stats = optimizer.end_session(session_id)

        assert stats["session_id"] == session_id
        assert optimizer.sessions[session_id]["active"] is False
        assert optimizer.sessions[session_id]["end_time"] is not None

    def test_end_nonexistent_session(self, optimizer):
        """Test ending a session that doesn't exist"""
        with pytest.raises(ValueError, match="Session .* not found"):
            optimizer.end_session("nonexistent123")


class TestOperationTracking:
    """Test operation tracking functionality"""

    def test_track_operation_basic(self, optimizer):
        """Test tracking a basic operation"""
        session_id = optimizer.start_session("track_test", budget=10000)

        result = optimizer.track_operation(
            session_id=session_id,
            operation="test_op",
            tokens_used=1000,
            compressed=False,
        )

        assert result["budget_remaining"] == 9000
        assert result["usage_percent"] == 10.0
        assert len(result["warnings"]) == 0

    def test_track_operation_with_compression(self, optimizer):
        """Test tracking operation with compression"""
        session_id = optimizer.start_session("compress_test")

        result = optimizer.track_operation(
            session_id=session_id,
            operation="compressed_op",
            tokens_used=5000,
            compressed=True,
            compression_ratio=0.35,
        )

        assert result["budget_remaining"] == 95000
        assert optimizer.sessions[session_id]["usage"] == 5000

    def test_budget_warnings(self, optimizer):
        """Test budget warning thresholds"""
        session_id = optimizer.start_session("warning_test", budget=10000)

        # 75% usage - should warn
        result = optimizer.track_operation(session_id, "op1", tokens_used=7500)
        assert "WARNING" in result["warnings"][0]

        # 90% usage - should be critical
        result = optimizer.track_operation(session_id, "op2", tokens_used=1500)
        assert "CRITICAL" in result["warnings"][0]

    def test_over_budget(self, optimizer):
        """Test exceeding budget"""
        session_id = optimizer.start_session("overbudget_test", budget=5000)

        result = optimizer.track_operation(session_id, "big_op", tokens_used=6000)

        assert result["over_budget"] is True
        assert result["budget_remaining"] == -1000

    def test_track_on_closed_session(self, optimizer):
        """Test tracking operation on closed session"""
        session_id = optimizer.start_session("closed_test")
        optimizer.end_session(session_id)

        with pytest.raises(ValueError, match="Session .* is closed"):
            optimizer.track_operation(session_id, "op", tokens_used=100)

    def test_track_on_nonexistent_session(self, optimizer):
        """Test tracking on nonexistent session"""
        with pytest.raises(ValueError, match="Session .* not found"):
            optimizer.track_operation("fake123", "op", tokens_used=100)


class TestCompression:
    """Test text compression functionality"""

    def test_compress_text_basic(self, optimizer):
        """Test basic text compression"""
        text = "Performance analysis shows warning"
        compressed, ratio = optimizer.compress_text(text, aggressive=False)

        # Should replace perf, warn
        assert "perf" in compressed.lower() or "\u26a1" in compressed
        assert ratio >= 0.0

    def test_compress_text_aggressive(self, optimizer):
        """Test aggressive compression"""
        text = (
            "The implementation of the configuration validation "
            "requires documentation"
        )
        compressed, ratio = optimizer.compress_text(text, aggressive=True)

        # Should remove articles and abbreviate
        assert "impl" in compressed or "cfg" in compressed
        assert "the" not in compressed.lower()
        assert ratio > 0.0

    def test_compress_text_empty(self, optimizer):
        """Test compressing empty text"""
        compressed, ratio = optimizer.compress_text("", aggressive=False)

        assert compressed == ""
        assert ratio == 0.0

    def test_compress_text_no_matches(self, optimizer):
        """Test text with no compression matches"""
        text = "xyz abc def"
        compressed, ratio = optimizer.compress_text(text, aggressive=False)

        assert compressed == text
        assert ratio == 0.0

    def test_compress_quick_function(self):
        """Test convenience compression function"""
        result = compress_quick("Performance warning")

        assert result is not None
        assert isinstance(result, str)


class TestStatistics:
    """Test statistics generation"""

    def test_get_stats_empty_db(self, optimizer):
        """Test stats for empty database"""
        stats = optimizer.get_stats()

        assert stats["total_sessions"] == 0
        assert stats["total_tokens_saved"] == 0
        assert stats["avg_compression_ratio"] == 0.0

    def test_get_stats_with_data(self, optimizer):
        """Test stats calculation with data"""
        # Create multiple sessions
        session1 = optimizer.start_session("session1", budget=10000)
        optimizer.track_operation(
            session1, "op1", tokens_used=1000, compressed=True, compression_ratio=0.3
        )
        optimizer.end_session(session1)

        session2 = optimizer.start_session("session2", budget=15000)
        optimizer.track_operation(
            session2, "op2", tokens_used=2000, compressed=True, compression_ratio=0.4
        )

        stats = optimizer.get_stats()

        assert stats["total_sessions"] == 2
        assert stats["active_sessions"] == 1  # session2 still active
        assert stats["total_tokens_saved"] > 0
        assert stats["compression_operations"] == 2

    def test_budget_overrun_tracking(self, optimizer):
        """Test tracking budget overruns"""
        session_id = optimizer.start_session("overrun_test", budget=1000)
        optimizer.track_operation(session_id, "big_op", tokens_used=2000)
        optimizer.end_session(session_id)

        stats = optimizer.get_stats()

        assert stats["budget_overruns"] == 1


class TestSessionStatistics:
    """Test session-level statistics"""

    def test_end_session_statistics(self, optimizer):
        """Test statistics generated when ending session"""
        session_id = optimizer.start_session("stats_test", budget=10000)

        # Track multiple operations
        optimizer.track_operation(
            session_id, "op1", tokens_used=1000, compressed=True, compression_ratio=0.3
        )
        optimizer.track_operation(session_id, "op2", tokens_used=500, compressed=False)
        optimizer.track_operation(
            session_id, "op3", tokens_used=2000, compressed=True, compression_ratio=0.4
        )

        stats = optimizer.end_session(session_id)

        assert stats["total_usage"] == 3500
        assert stats["budget_remaining"] == 6500
        assert stats["total_operations"] == 3
        assert stats["compressed_operations"] == 2
        assert stats["avg_compression_ratio"] > 0
        assert stats["total_savings"] > 0

    def test_session_stats_no_compression(self, optimizer):
        """Test stats for session with no compression"""
        session_id = optimizer.start_session("no_compress_test")
        optimizer.track_operation(session_id, "op", tokens_used=1000)

        stats = optimizer.end_session(session_id)

        assert stats["compressed_operations"] == 0
        assert stats["avg_compression_ratio"] == 0.0
        assert stats["total_savings"] == 0


class TestPersistence:
    """Test database persistence"""

    def test_save_and_load(self, temp_db):
        """Test saving and loading database"""
        optimizer1 = TokenOptimizer(db_path=temp_db)
        session_id = optimizer1.start_session("persist_test")
        optimizer1.track_operation(session_id, "op", tokens_used=1000)

        # Create new instance (should load from disk)
        optimizer2 = TokenOptimizer(db_path=temp_db)

        assert session_id in optimizer2.sessions
        assert optimizer2.sessions[session_id]["usage"] == 1000

    def test_corrupted_db_recovery(self, temp_db):
        """Test recovery from corrupted database"""
        # Create corrupted JSON file
        Path(temp_db).write_text("{ invalid json", encoding="utf-8")

        # Should recover gracefully
        optimizer = TokenOptimizer(db_path=temp_db)

        assert optimizer.sessions == {}


class TestObsidianIntegration:
    """Test Obsidian MOC generation"""

    def test_generate_obsidian_moc(self, optimizer):
        """Test Obsidian MOC generation"""
        session_id = optimizer.start_session("moc_test", budget=10000)
        optimizer.track_operation(
            session_id, "op", tokens_used=1000, compressed=True, compression_ratio=0.3
        )

        moc = optimizer.generate_obsidian_moc()

        assert "Token Optimizer - MOC" in moc
        assert "Total Sessions" in moc
        assert "Total Tokens Saved" in moc
        assert "moc_test" in moc

    def test_export_to_obsidian(self, optimizer, tmp_path):
        """Test exporting to Obsidian vault"""
        session_id = optimizer.start_session("export_test")
        optimizer.track_operation(session_id, "op", tokens_used=100)

        vault_path = tmp_path / "obsidian_vault"
        vault_path.mkdir()

        optimizer.export_to_obsidian(str(vault_path))

        moc_file = vault_path / "Token_Optimizer.md"
        assert moc_file.exists()

        content = moc_file.read_text(encoding="utf-8")
        assert "Token Optimizer - MOC" in content


class TestCompressionSymbols:
    """Test compression symbol mappings"""

    def test_compression_symbols_init(self, optimizer):
        """Test compression symbols initialization"""
        assert len(optimizer.compression_symbols) > 0
        assert "->" in optimizer.compression_symbols
        assert "perf" in optimizer.compression_symbols

    def test_symbol_application(self, optimizer):
        """Test symbol application in compression"""
        text = "performance -> warning"
        compressed, _ = optimizer.compress_text(text, aggressive=False)

        # Should apply symbols
        assert compressed != text


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_session_name(self, optimizer):
        """Test session with empty name"""
        session_id = optimizer.start_session("")

        assert session_id is not None
        assert optimizer.sessions[session_id]["name"] == ""

    def test_zero_budget(self, optimizer):
        """Test session with zero budget"""
        session_id = optimizer.start_session("zero_budget", budget=0)

        result = optimizer.track_operation(session_id, "op", tokens_used=1)

        # With 0 budget and 1 token used, usage > budget
        assert optimizer.sessions[session_id]["usage"] == 1
        assert result["budget_remaining"] == -1

    def test_negative_tokens(self, optimizer):
        """Test tracking with negative tokens (edge case)"""
        session_id = optimizer.start_session("negative_test")

        # System should allow this (might represent corrections)
        optimizer.track_operation(session_id, "op", tokens_used=-100)

        assert optimizer.sessions[session_id]["usage"] == -100

    def test_very_large_budget(self, optimizer):
        """Test with very large budget"""
        session_id = optimizer.start_session("large_budget", budget=10000000)

        result = optimizer.track_operation(session_id, "op", tokens_used=1000)

        assert result["usage_percent"] < 1.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=token_optimizer",
            "--cov-report=term-missing",
        ]
    )
