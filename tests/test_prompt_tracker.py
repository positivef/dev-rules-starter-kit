"""
Unit tests for Prompt Tracker
Target coverage: >= 90%
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_tracker import PromptTracker, track_quick


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing"""
    db_path = tmp_path / "test_prompts.json"
    return str(db_path)


@pytest.fixture
def tracker(temp_db):
    """PromptTracker instance with temp database"""
    return PromptTracker(db_path=temp_db)


class TestInteractionTracking:
    """Test interaction tracking functionality"""

    def test_track_basic_interaction(self, tracker):
        """Test basic interaction tracking"""
        interaction_id = tracker.track_interaction(
            prompt="Test prompt",
            response="Test response",
            model="claude-sonnet-4",
            tokens_input=100,
            tokens_output=200,
            success=True,
            tags=["test"],
        )

        assert interaction_id is not None
        assert len(interaction_id) == 8  # SHA-256[:8]
        assert interaction_id in tracker.prompts
        assert tracker.prompts[interaction_id]["success"] is True

    def test_track_with_metadata(self, tracker):
        """Test tracking with custom metadata"""
        interaction_id = tracker.track_interaction(
            prompt="Implement feature",
            response="Done",
            tokens_input=100,
            tokens_output=100,
            metadata={"feature": "error_learner", "complexity": "high"},
        )

        assert tracker.prompts[interaction_id]["metadata"]["feature"] == "error_learner"
        assert tracker.prompts[interaction_id]["metadata"]["complexity"] == "high"

    def test_cost_calculation(self, tracker):
        """Test token cost calculation"""
        interaction_id = tracker.track_interaction(
            prompt="Test",
            response="Response",
            model="claude-sonnet-4",
            tokens_input=1000,  # 1K tokens
            tokens_output=2000,  # 2K tokens
        )

        # $0.003 per 1K input + $0.015 per 1K output (2K)
        expected_cost = (1 * 0.003) + (2 * 0.015)  # 0.033
        assert tracker.prompts[interaction_id]["cost_usd"] == pytest.approx(
            expected_cost, rel=0.01
        )


class TestStatistics:
    """Test statistics generation"""

    def test_get_stats_empty_db(self, tracker):
        """Test stats for empty database"""
        stats = tracker.get_stats()

        assert stats["total_interactions"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_cost"] == 0.0
        assert stats["success_rate"] == 0.0

    def test_get_stats_with_data(self, tracker):
        """Test stats calculation with data"""
        # Add multiple interactions
        tracker.track_interaction(
            "Prompt 1", "Response 1", tokens_input=100, tokens_output=200, success=True
        )
        tracker.track_interaction(
            "Prompt 2",
            "Response 2",
            tokens_input=150,
            tokens_output=250,
            success=False,
        )

        stats = tracker.get_stats()

        assert stats["total_interactions"] == 2
        assert stats["total_tokens"] == 700  # (100+200) + (150+250)
        assert stats["success_rate"] == 50.0  # 1/2

    def test_stats_filtering_by_days(self, tracker):
        """Test stats filtering by time period"""
        tracker.track_interaction(
            "Recent", "Response", tokens_input=100, tokens_output=100, tags=["recent"]
        )

        # Filter last 7 days
        stats = tracker.get_stats(days=7)
        assert stats["total_interactions"] == 1

    def test_stats_filtering_by_tags(self, tracker):
        """Test stats filtering by tags"""
        tracker.track_interaction(
            "Prompt 1", "Response 1", tokens_input=100, tokens_output=100, tags=["code"]
        )
        tracker.track_interaction(
            "Prompt 2", "Response 2", tokens_input=100, tokens_output=100, tags=["docs"]
        )

        stats = tracker.get_stats(tags=["code"])
        assert stats["total_interactions"] == 1


class TestPatternAnalysis:
    """Test pattern analysis features"""

    def test_find_effective_patterns(self, tracker):
        """Test finding patterns with high success rates"""
        # Add interactions with tags
        for i in range(5):
            tracker.track_interaction(
                f"Code prompt {i}",
                f"Response {i}",
                tokens_input=100,
                tokens_output=100,
                success=True,
                tags=["coding"],
            )

        for i in range(2):
            tracker.track_interaction(
                f"Docs prompt {i}",
                f"Response {i}",
                tokens_input=100,
                tokens_output=100,
                success=False,
                tags=["documentation"],
            )

        effective = tracker.find_effective_patterns(min_success_rate=80.0)

        assert len(effective) > 0
        assert effective[0]["pattern"] == "coding"
        assert effective[0]["success_rate"] == 100.0

    def test_find_inefficient_prompts(self, tracker):
        """Test finding high-token-usage prompts"""
        # Add normal prompt
        tracker.track_interaction(
            "Normal prompt", "Response", tokens_input=1000, tokens_output=2000
        )

        # Add inefficient prompt
        tracker.track_interaction(
            "Very long inefficient prompt",
            "Very long response",
            tokens_input=8000,
            tokens_output=8000,
            tags=["inefficient"],
        )

        inefficient = tracker.find_inefficient_prompts(token_threshold=10000)

        assert len(inefficient) == 1
        assert inefficient[0]["tokens"] == 16000
        assert "inefficient" in inefficient[0]["tags"]


class TestPersistence:
    """Test database persistence"""

    def test_save_and_load(self, temp_db):
        """Test saving and loading database"""
        tracker1 = PromptTracker(db_path=temp_db)
        interaction_id = tracker1.track_interaction(
            "Test", "Response", tokens_input=100, tokens_output=100
        )

        # Create new instance (should load from disk)
        tracker2 = PromptTracker(db_path=temp_db)

        assert interaction_id in tracker2.prompts
        assert tracker2.prompts[interaction_id]["prompt"] == "Test"

    def test_corrupted_db_recovery(self, temp_db):
        """Test recovery from corrupted database"""
        # Create corrupted JSON file
        Path(temp_db).write_text("{ invalid json", encoding="utf-8")

        # Should recover gracefully
        tracker = PromptTracker(db_path=temp_db)

        assert tracker.prompts == {}


class TestObsidianIntegration:
    """Test Obsidian MOC generation"""

    def test_generate_obsidian_moc(self, tracker):
        """Test Obsidian MOC generation"""
        tracker.track_interaction(
            "Test prompt",
            "Test response",
            tokens_input=1000,
            tokens_output=2000,
            success=True,
            tags=["test"],
        )

        moc = tracker.generate_obsidian_moc()

        assert "Prompt Tracker - MOC" in moc
        assert "Total Interactions" in moc
        assert "Total Tokens" in moc

    def test_export_to_obsidian(self, tracker, tmp_path):
        """Test exporting to Obsidian vault"""
        tracker.track_interaction(
            "Test", "Response", tokens_input=100, tokens_output=100
        )

        vault_path = tmp_path / "obsidian_vault"
        vault_path.mkdir()

        tracker.export_to_obsidian(str(vault_path))

        moc_file = vault_path / "Prompt_Tracker.md"
        assert moc_file.exists()

        content = moc_file.read_text(encoding="utf-8")
        assert "Prompt Tracker - MOC" in content


class TestQuickTracking:
    """Test convenience function"""

    def test_track_quick(self, temp_db, monkeypatch):
        """Test quick tracking function"""
        # Mock PromptTracker to use temp_db
        monkeypatch.setattr(
            "prompt_tracker.PromptTracker", lambda: PromptTracker(db_path=temp_db)
        )

        track_quick(prompt="Quick test", response="Quick response", success=True)

        # Verify tracked
        tracker = PromptTracker(db_path=temp_db)
        assert len(tracker.prompts) == 1


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_prompt(self, tracker):
        """Test handling of empty prompt"""
        interaction_id = tracker.track_interaction(prompt="", response="Response")

        assert interaction_id is not None

    def test_very_long_prompt(self, tracker):
        """Test handling of very long prompt"""
        long_prompt = "A" * 100000
        interaction_id = tracker.track_interaction(
            prompt=long_prompt, response="Response"
        )

        assert interaction_id is not None
        assert tracker.prompts[interaction_id]["prompt"] == long_prompt

    def test_unknown_model_cost(self, tracker):
        """Test cost calculation for unknown model"""
        interaction_id = tracker.track_interaction(
            prompt="Test",
            response="Response",
            model="unknown-model",
            tokens_input=1000,
            tokens_output=1000,
        )

        # Should default to 0.0 for unknown models
        assert tracker.prompts[interaction_id]["cost_usd"] == 0.0

    def test_unicode_in_prompt(self, tracker):
        """Test Unicode characters in prompt"""
        interaction_id = tracker.track_interaction(
            prompt="Test with Korean",
            response="Response",
        )

        assert interaction_id is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--cov=prompt_tracker", "--cov-report=term-missing"])
