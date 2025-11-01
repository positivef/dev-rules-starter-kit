#!/usr/bin/env python3
"""
Security Tests for PromptCompressor

Purpose: Verify security improvements from multi-agent review

Constitutional Compliance:
- [P3] Test-First Development
- [P5] Windows UTF-8: No emoji
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_compressor import PromptCompressor, MAX_INPUT_SIZE
import pytest
import logging


class TestInputValidation:
    """Test input size validation and security checks"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_accepts_normal_input(self):
        """Normal inputs should work without issues"""
        prompt = "Please implement authentication feature" * 100  # ~4KB
        result = self.compressor.compress(prompt)
        assert result is not None
        assert result.compressed is not None

    def test_rejects_oversized_input(self):
        """Inputs exceeding MAX_INPUT_SIZE should raise ValueError"""
        # Create input larger than 1MB
        huge_prompt = "x" * (MAX_INPUT_SIZE + 1000)

        with pytest.raises(ValueError) as exc_info:
            self.compressor.compress(huge_prompt)

        assert "exceeds maximum size" in str(exc_info.value)

    def test_max_size_boundary(self):
        """Input at exactly MAX_INPUT_SIZE should work"""
        boundary_prompt = "x" * MAX_INPUT_SIZE
        result = self.compressor.compress(boundary_prompt)
        assert result is not None


class TestSecretDetection:
    """Test detection of potential secrets in prompts"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_detects_api_key_pattern(self, caplog):
        """Should warn about potential API keys"""
        with caplog.at_level(logging.WARNING):
            prompt = "Use this api_key for authentication"
            self.compressor.compress(prompt)

        assert any("secret detected" in record.message.lower() for record in caplog.records)

    def test_detects_password_pattern(self, caplog):
        """Should warn about potential passwords"""
        with caplog.at_level(logging.WARNING):
            prompt = "Set the password to secure123"
            self.compressor.compress(prompt)

        assert any("secret detected" in record.message.lower() for record in caplog.records)

    def test_detects_secret_pattern(self, caplog):
        """Should warn about potential secrets"""
        with caplog.at_level(logging.WARNING):
            prompt = "Store the secret in environment"
            self.compressor.compress(prompt)

        assert any("secret detected" in record.message.lower() for record in caplog.records)

    def test_no_warning_for_safe_content(self, caplog):
        """Safe content should not trigger warnings"""
        with caplog.at_level(logging.WARNING):
            prompt = "Implement authentication feature for the application"
            self.compressor.compress(prompt)

        # Should have no secret detection warnings
        secret_warnings = [r for r in caplog.records if "secret detected" in r.message.lower()]
        assert len(secret_warnings) == 0


class TestErrorHandling:
    """Test error handling in critical operations"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_learn_from_success_handles_errors(self):
        """learn_from_success should not crash on errors"""
        # This should return False or handle gracefully
        result = self.compressor.learn_from_success("", "", True)
        assert isinstance(result, bool)

    def test_invalid_compression_level_handled(self):
        """Invalid compression level should use default"""
        compressor = PromptCompressor(compression_level="invalid")
        result = compressor.compress("Test prompt")
        assert result is not None


class TestPerformanceOptimizations:
    """Test that performance optimizations are working"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_patterns_precompiled(self):
        """Regex patterns should be pre-compiled"""
        assert hasattr(self.compressor, "_compiled_abbrevs")
        assert hasattr(self.compressor, "_compiled_rules")
        assert len(self.compressor._compiled_abbrevs) > 0
        assert len(self.compressor._compiled_rules) > 0

    def test_early_termination_works(self):
        """Early termination should stop compression when target reached"""
        # Use a very simple prompt that compresses easily
        prompt = "Please please please implement this"
        result = self.compressor.compress(prompt, target_reduction=10.0)

        # Should have stopped early (not applied all rules)
        # This is a heuristic check
        assert result.savings_pct >= 10.0

    def test_optimized_methods_exist(self):
        """Optimized methods should exist"""
        assert hasattr(self.compressor, "_apply_abbreviations_optimized")
        assert hasattr(self.compressor, "_apply_compression_rules_optimized")
        assert hasattr(self.compressor, "_check_target_reached")
        assert hasattr(self.compressor, "_build_result")


class TestBackwardsCompatibility:
    """Test that existing functionality still works"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_legacy_abbreviations_method(self):
        """Legacy _apply_abbreviations should still work"""
        text = "Please implement authentication"
        result, rules = self.compressor._apply_abbreviations(text)
        assert "auth" in result.lower()

    def test_legacy_compression_rules_method(self):
        """Legacy _apply_compression_rules should still work"""
        text = "This  has   multiple    spaces"
        result, rules = self.compressor._apply_compression_rules(text)
        assert "  " not in result  # Multiple spaces removed
