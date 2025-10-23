#!/usr/bin/env python3
"""
Test suite for PromptCompressor

Constitutional Compliance:
- [P3] Test-First Development: Tests written before implementation integration
- [P5] Windows UTF-8: No emoji in code
- [P8] 90% coverage target
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_compressor import (
    PromptCompressor,
    compress_prompt,
)


class TestCompressionBasics:
    """Test basic compression functionality"""

    def setup_method(self):
        """Setup before each test"""
        self.compressor = PromptCompressor(compression_level="medium")

    def test_compressor_initialization(self):
        """Test that compressor initializes correctly"""
        assert self.compressor is not None
        assert self.compressor.compression_level == "medium"
        assert len(self.compressor.abbreviations) > 0
        assert len(self.compressor.compression_rules) > 0

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts"""
        result = self.compressor.compress("")
        assert result.original == ""
        assert result.compressed == ""
        assert result.savings_pct == 0.0

    def test_whitespace_only_prompt(self):
        """Test handling of whitespace-only prompts"""
        result = self.compressor.compress("   \n\t   ")
        assert result.compressed.strip() == ""

    def test_simple_abbreviation(self):
        """Test basic abbreviation replacement"""
        prompt = "Please implement authentication for the application"
        result = self.compressor.compress(prompt)

        assert "auth" in result.compressed.lower()
        assert "app" in result.compressed.lower()
        assert result.savings_pct > 0


class TestCompressionLevels:
    """Test different compression levels"""

    def test_light_compression(self):
        """Test light compression (20% target)"""
        compressor = PromptCompressor(compression_level="light")
        prompt = "Please implement the authentication feature for the application"
        result = compressor.compress(prompt)

        assert result.original_tokens > result.compressed_tokens
        assert len(result.compression_rules) > 0

    def test_medium_compression(self):
        """Test medium compression (35% target)"""
        compressor = PromptCompressor(compression_level="medium")
        prompt = "I would like you to create a new database schema for the user management system with proper validation"
        result = compressor.compress(prompt)

        assert result.savings_pct >= 20  # Should save at least 20%
        assert "db" in result.compressed or "database" in result.compressed

    def test_aggressive_compression(self):
        """Test aggressive compression (50% target)"""
        compressor = PromptCompressor(compression_level="aggressive")
        prompt = (
            "Can you please make sure that the performance optimization "
            "is applied to all the critical files in the repository?"
        )
        result = compressor.compress(prompt)

        assert result.savings_pct >= 30  # Should save at least 30%
        assert len(result.compressed) < len(result.original) * 0.7


class TestAbbreviations:
    """Test abbreviation system"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_technical_abbreviations(self):
        """Test technical term abbreviations"""
        test_cases = [
            ("implementation", "impl"),
            ("configuration", "cfg"),
            ("architecture", "arch"),
            ("performance", "perf"),
            ("database", "db"),
            ("authentication", "auth"),
        ]

        for full, abbrev in test_cases:
            prompt = f"Work on the {full} system"
            result = self.compressor.compress(prompt)
            assert abbrev in result.compressed.lower()

    def test_politeness_removal(self):
        """Test removal of unnecessary politeness"""
        prompts = [
            "Please implement this feature",
            "I would like you to create this",
            "Can you help me with this",
            "Could you please fix this",
        ]

        for prompt in prompts:
            result = self.compressor.compress(prompt)
            # Politeness words should be removed
            assert "please" not in result.compressed.lower()
            assert "would like" not in result.compressed.lower()

    def test_redundant_phrase_removal(self):
        """Test removal of redundant phrases"""
        prompt = "Make sure that you ensure that the implementation is correct"
        result = self.compressor.compress(prompt)

        # Redundant phrases should be removed
        assert "make sure" not in result.compressed.lower()
        assert "ensure that" not in result.compressed.lower()


class TestCompressionRules:
    """Test regex-based compression rules"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_multiple_spaces_collapse(self):
        """Test collapsing of multiple spaces"""
        prompt = "This  has   multiple    spaces"
        result = self.compressor.compress(prompt)

        assert "  " not in result.compressed  # No double spaces

    def test_list_optimization(self):
        """Test numbered list optimization"""
        prompt = "1. First item 2. Second item 3. Third item"
        result = self.compressor.compress(prompt)

        # Should compact list format
        assert "1)" in result.compressed or "1." in result.compressed


class TestTokenEstimation:
    """Test token counting accuracy"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_token_estimation_basic(self):
        """Test basic token estimation"""
        tokens = self.compressor._estimate_tokens("Hello world")
        assert tokens > 0
        assert tokens < 10  # Should be roughly 2-3 tokens

    def test_token_estimation_long_text(self):
        """Test token estimation for longer text"""
        long_text = " ".join(["word"] * 100)
        tokens = self.compressor._estimate_tokens(long_text)
        assert tokens >= 100  # At least 1 token per word
        assert tokens <= 200  # But not too many


class TestCompressionMetrics:
    """Test compression metrics calculation"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_savings_calculation(self):
        """Test savings percentage calculation"""
        prompt = "Please implement the authentication feature for the application"
        result = self.compressor.compress(prompt)

        assert result.original_tokens > 0
        assert result.compressed_tokens > 0
        assert result.compressed_tokens < result.original_tokens
        assert 0 <= result.savings_pct <= 100

    def test_compression_rules_tracking(self):
        """Test that compression rules are tracked"""
        prompt = "Please implement authentication for the application"
        result = self.compressor.compress(prompt)

        assert len(result.compression_rules) > 0
        assert any("abbrev" in rule for rule in result.compression_rules)


class TestLearning:
    """Test learning from successful compressions"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")
        # Clean learned patterns for testing
        if self.compressor.learned_patterns_path.exists():
            self.compressor.learned_patterns_path.unlink()
        self.compressor.learned_patterns = {}

    def test_learn_from_success(self):
        """Test learning from successful compression"""
        original = "Create a user authentication system"
        compressed = "Create user auth system"

        self.compressor.learn_from_success(original, compressed, success=True)

        assert len(self.compressor.learned_patterns) == 1

    def test_ignore_failures(self):
        """Test that failures are not learned"""
        original = "Some prompt"
        compressed = "Compressed"

        self.compressor.learn_from_success(original, compressed, success=False)

        assert len(self.compressor.learned_patterns) == 0

    def test_success_rate_calculation(self):
        """Test success rate calculation for learned patterns"""
        original = "Test prompt"
        compressed = "Compressed"

        # Learn multiple times
        for _ in range(3):
            self.compressor.learn_from_success(original, compressed, success=True)

        # Check success rate
        pattern_id = list(self.compressor.learned_patterns.keys())[0]
        pattern = self.compressor.learned_patterns[pattern_id]

        assert pattern["success_rate"] == 100.0
        assert pattern["success_count"] == 3


class TestStatistics:
    """Test compressor statistics"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_get_stats(self):
        """Test statistics retrieval"""
        stats = self.compressor.get_stats()

        assert "total_learned_patterns" in stats
        assert "high_success_patterns" in stats
        assert "abbreviations_count" in stats
        assert "compression_rules_count" in stats
        assert "compression_level" in stats

        assert stats["compression_level"] == "medium"
        assert stats["abbreviations_count"] > 0
        assert stats["compression_rules_count"] > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_very_short_prompt(self):
        """Test very short prompts"""
        result = self.compressor.compress("Do it")
        assert result.compressed is not None
        assert len(result.compressed) > 0

    def test_very_long_prompt(self):
        """Test very long prompts"""
        long_prompt = " ".join(["Please implement the authentication feature for the application" for _ in range(10)])
        result = self.compressor.compress(long_prompt)

        assert result.savings_pct > 0
        assert result.compressed_tokens < result.original_tokens

    def test_unicode_handling(self):
        """Test Unicode character handling (Korean, Japanese, etc.)"""
        # Note: No emoji per P5, but other Unicode is allowed
        prompt = "Implement \ud14c\uc2a4\ud2b8 feature"
        result = self.compressor.compress(prompt)

        assert result.compressed is not None

    def test_special_characters(self):
        """Test special character handling"""
        prompt = "Implement feature: @user_auth #priority-1"
        result = self.compressor.compress(prompt)

        assert result.compressed is not None


class TestConvenienceFunction:
    """Test convenience function"""

    def test_compress_prompt_function(self):
        """Test quick compress_prompt function"""
        prompt = "Please implement authentication for the application"
        compressed = compress_prompt(prompt, level="medium")

        assert compressed is not None
        assert len(compressed) < len(prompt)
        assert "auth" in compressed.lower()


class TestRealWorldPrompts:
    """Test with real-world prompt examples"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_implementation_request(self):
        """Test typical implementation request"""
        prompt = (
            "Please implement the user authentication feature for the web "
            "application with proper error handling and validation"
        )
        result = self.compressor.compress(prompt)

        assert result.savings_pct >= 25  # Should save at least 25%
        assert "auth" in result.compressed.lower()
        assert "app" in result.compressed.lower()

    def test_refactoring_request(self):
        """Test refactoring request"""
        prompt = "I would like you to refactor the database access layer to improve performance and reduce complexity"
        result = self.compressor.compress(prompt)

        assert result.savings_pct >= 25
        assert "db" in result.compressed.lower()
        assert "perf" in result.compressed.lower()

    def test_bug_fix_request(self):
        """Test bug fix request"""
        prompt = (
            "Can you please fix the issue in the authentication module where users cannot log in with valid credentials?"
        )
        result = self.compressor.compress(prompt)

        assert result.savings_pct >= 20
        assert len(result.compressed) < len(prompt)
