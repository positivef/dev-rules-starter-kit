#!/usr/bin/env python3
"""
Semantic Preservation Tests for PromptCompressor

Purpose: Verify that compression does NOT lose critical meaning or context

Constitutional Compliance:
- [P3] Test-First Development
- [P5] Windows UTF-8: No emoji
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_compressor import PromptCompressor


class TestSemanticPreservation:
    """Test that compression preserves essential meaning"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_preserves_core_action_verbs(self):
        """Verify core action verbs are never removed"""
        test_cases = [
            ("implement", "implement"),
            ("refactor", "refactor"),
            ("fix", "fix"),
            ("test", "test"),
            ("deploy", "deploy"),
            ("analyze", "analyze"),
        ]

        for verb, expected in test_cases:
            prompt = f"Please {verb} the feature"
            result = self.compressor.compress(prompt)
            assert expected in result.compressed.lower(), f"Core verb '{verb}' lost in compression"

    def test_preserves_technical_targets(self):
        """Verify technical targets (files, modules) are preserved"""
        test_cases = [
            "Fix the bug in auth.py",
            "Refactor database/models.py",
            "Test the UserService class",
        ]

        for prompt in test_cases:
            result = self.compressor.compress(prompt)

            # File names should be preserved
            if ".py" in prompt:
                assert ".py" in result.compressed or "py" in result.compressed

    def test_preserves_critical_modifiers(self):
        """Verify critical modifiers that change meaning are preserved"""
        test_cases = [
            ("NOT implement", "not"),  # Negation is critical
            ("MUST implement", "must"),  # Obligation is critical
            ("CANNOT access", "cannot"),  # Restriction is critical
        ]

        for prompt, critical_word in test_cases:
            result = self.compressor.compress(prompt)
            assert critical_word in result.compressed.lower(), f"Critical modifier '{critical_word}' lost"

    def test_preserves_numbers_and_quantities(self):
        """Verify numbers and quantities are preserved"""
        test_cases = [
            "Create 5 test cases",
            "Limit to 100 records",
            "Set timeout to 30 seconds",
        ]

        for prompt in test_cases:
            result = self.compressor.compress(prompt)

            # Extract numbers from original and compressed
            import re

            orig_nums = set(re.findall(r"\d+", prompt))
            comp_nums = set(re.findall(r"\d+", result.compressed))

            assert orig_nums == comp_nums, f"Numbers lost: {orig_nums} -> {comp_nums}"

    def test_preserves_technical_terms(self):
        """Verify domain-specific technical terms are preserved or abbreviated"""
        test_cases = [
            ("authentication", ["auth", "authentication"]),
            ("database", ["db", "database"]),
            ("configuration", ["cfg", "config", "configuration"]),
            ("performance", ["perf", "performance"]),
        ]

        for term, acceptable_forms in test_cases:
            prompt = f"Improve the {term} system"
            result = self.compressor.compress(prompt)

            assert any(
                form in result.compressed.lower() for form in acceptable_forms
            ), f"Technical term '{term}' not preserved in acceptable form"


class TestMeaningDistortion:
    """Test for meaning distortion (what NOT to do)"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_no_action_reversal(self):
        """Ensure compression doesn't reverse the action"""
        test_cases = [
            "Add authentication",
            "Remove deprecated code",
            "Enable logging",
            "Disable caching",
        ]

        for prompt in test_cases:
            result = self.compressor.compress(prompt)

            # Extract first verb
            words = prompt.lower().split()
            action = words[0]  # add, remove, enable, disable

            # Action should be preserved
            assert action in result.compressed.lower(), f"Action '{action}' lost, may cause reversal"

    def test_no_target_confusion(self):
        """Ensure compression doesn't confuse similar targets"""
        test_cases = [
            ("Fix user authentication", "auth"),
            ("Fix user authorization", "authz"),
        ]

        for prompt, expected_term in test_cases:
            result = self.compressor.compress(prompt)

            # Should NOT confuse auth/authz
            assert expected_term in result.compressed.lower() or (
                "authentication" in result.compressed.lower()
                if expected_term == "auth"
                else "authorization" in result.compressed.lower()
            )

    def test_no_scope_loss(self):
        """Ensure scope indicators are preserved"""
        test_cases = [
            ("Fix ALL bugs", "all"),
            ("Update ONLY the header", "only"),
            ("Test EACH function", "each"),
        ]

        for prompt, scope_word in test_cases:
            result = self.compressor.compress(prompt)

            # Scope words are important - should be preserved
            # (or entire scope should be clear from context)
            if scope_word in ["all", "only", "each"]:
                # These are important enough to keep
                assert (
                    scope_word in result.compressed.lower()
                    or len(result.compressed.split()) < 5  # very short = implied scope
                )


class TestCriticalInformationRetention:
    """Test retention of critical information categories"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_retains_error_context(self):
        """Verify error-related context is retained"""
        prompt = "Fix the NullPointerException in UserService.getUser() method"
        result = self.compressor.compress(prompt)

        # Critical info: Fix, error type, location
        assert "fix" in result.compressed.lower()
        assert "nullpointer" in result.compressed.lower() or "null" in result.compressed.lower()
        assert "userservice" in result.compressed.lower() or "user" in result.compressed.lower()

    def test_retains_performance_metrics(self):
        """Verify performance metrics are retained"""
        prompt = "Optimize the query to run under 100ms with caching"
        result = self.compressor.compress(prompt)

        # Critical info: opt action, timing, solution
        assert "opt" in result.compressed.lower() or "optimize" in result.compressed.lower()
        assert "100" in result.compressed or "ms" in result.compressed
        assert "cach" in result.compressed.lower()  # cache/caching

    def test_retains_security_context(self):
        """Verify security-related context is retained"""
        prompt = "Add input validation to prevent SQL injection in login form"
        result = self.compressor.compress(prompt)

        # Critical info: add, validation, sql injection, login
        assert "add" in result.compressed.lower()
        assert "val" in result.compressed.lower() or "validation" in result.compressed.lower()
        assert "sql" in result.compressed.lower()
        assert "login" in result.compressed.lower()


class TestCompressionSafety:
    """Test safety limits and fallbacks"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_minimal_compression_on_short_prompts(self):
        """Short prompts should compress minimally to avoid information loss"""
        short_prompts = [
            "Fix bug",
            "Add test",
            "Deploy now",
        ]

        for prompt in short_prompts:
            result = self.compressor.compress(prompt)

            # Should retain most of the content
            assert len(result.compressed.split()) >= len(prompt.split()) - 1

    def test_preserves_critical_short_prompts(self):
        """Very short critical prompts should be barely touched"""
        critical_prompts = [
            "Emergency fix",
            "Rollback deployment",
            "Stop server",
        ]

        for prompt in critical_prompts:
            result = self.compressor.compress(prompt)

            # Should preserve almost everything
            orig_words = set(prompt.lower().split())
            comp_words = set(result.compressed.lower().split())

            # At least 50% of original words should remain
            overlap = orig_words & comp_words
            assert len(overlap) >= len(orig_words) * 0.5


class TestObjectiveMetrics:
    """Objective metrics for compression quality"""

    def setup_method(self):
        self.compressor = PromptCompressor(compression_level="medium")

    def test_information_density_increases(self):
        """Compression should increase information density (meaning per token)"""
        prompt = (
            "Please make sure that you implement the user authentication "
            "feature for the web application with proper error handling"
        )
        result = self.compressor.compress(prompt)

        # Key information units: implement, user, auth, web, app, error, handling
        key_info = ["implement", "user", "auth", "web", "app", "error", "handle"]

        preserved_count = sum(1 for info in key_info if info in result.compressed.lower())

        # Should preserve at least 80% of key information
        assert preserved_count >= len(key_info) * 0.8, f"Only {preserved_count}/{len(key_info)} key info preserved"

    def test_compression_consistency(self):
        """Same prompt should compress consistently"""
        prompt = "Implement authentication feature"

        results = [self.compressor.compress(prompt).compressed for _ in range(3)]

        # All results should be identical
        assert len(set(results)) == 1, "Compression is not deterministic"

    def test_reversibility_of_abbreviations(self):
        """Abbreviations should be unambiguous (reversible)"""
        # Test that auth -> authentication is clear
        # Test that db -> database is clear
        # etc.

        abbrev_map = {
            "auth": "authentication",
            "db": "database",
            "cfg": "configuration",
            "perf": "performance",
        }

        for abbrev, full in abbrev_map.items():
            prompt = f"Fix the {full} system"
            result = self.compressor.compress(prompt)

            # Should use abbreviation
            assert abbrev in result.compressed.lower()

            # Abbreviation should be unambiguous in context
            # (This is a basic check - real test would be AI interpretation)
            assert "fix" in result.compressed.lower()
            assert "system" in result.compressed.lower() or "sys" in result.compressed.lower()
