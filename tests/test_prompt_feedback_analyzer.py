#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Prompt Feedback Analyzer - P8 (Test First) Compliance

Tests cover:
- Clarity analysis
- Logic flow detection
- Context completeness
- Structure evaluation
- Feedback generation
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_feedback_analyzer import PromptFeedbackAnalyzer, PromptAnalysis


class TestPromptFeedbackAnalyzer:
    """Test suite for PromptFeedbackAnalyzer"""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer instance with temp directory"""
        return PromptFeedbackAnalyzer(learning_dir=tmp_path / "learning")

    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None
        assert analyzer.learning_dir.exists()

    def test_analyze_basic_prompt(self, analyzer):
        """Test basic prompt analysis"""
        prompt = "Fix the bug in the login function"
        analysis = analyzer.analyze(prompt)

        assert isinstance(analysis, PromptAnalysis)
        assert analysis.original_prompt == prompt
        assert 0 <= analysis.overall_score <= 100
        assert analysis.word_count == 7
        assert analysis.sentence_count == 1

    def test_clarity_scoring(self, analyzer):
        """Test clarity score calculation"""
        # Vague prompt should have low clarity
        vague_prompt = "fix stuff and make it better somehow"
        vague_analysis = analyzer.analyze(vague_prompt)

        # Clear prompt should have high clarity
        clear_prompt = "Fix the authentication timeout bug in auth.py line 45"
        clear_analysis = analyzer.analyze(clear_prompt)

        assert clear_analysis.clarity_score > vague_analysis.clarity_score
        assert "somehow" in vague_analysis.ambiguous_terms
        assert "stuff" in vague_analysis.ambiguous_terms

    def test_logic_flow_detection(self, analyzer):
        """Test logical flow analysis"""
        # Prompt with logical connectors - should score high
        logical_prompt = "First analyze the data, then generate the report, finally send the email"
        logical_analysis = analyzer.analyze(logical_prompt)

        # Test that logical prompt gets bonus points
        assert logical_analysis.logic_score >= 90

    def test_context_completeness(self, analyzer):
        """Test context analysis"""
        # Prompt with context
        contextual_prompt = "Using Python 3.9 with pandas, process the CSV file (max 100MB)"
        contextual_analysis = analyzer.analyze(contextual_prompt)

        # Prompt without context - completely vague
        no_context_prompt = "do the task"
        no_context_analysis = analyzer.analyze(no_context_prompt)

        # Contextual prompt should score significantly higher
        assert contextual_analysis.context_score > no_context_analysis.context_score

    def test_structure_evaluation(self, analyzer):
        """Test structure scoring"""
        # Well-structured prompt with numbered list
        structured = """1. Load the data from database
2. Clean null values
3. Generate visualization
4. Export as PDF"""
        structured_analysis = analyzer.analyze(structured)

        # Structured prompts should score high
        assert structured_analysis.structure_score >= 90

    def test_improvement_generation(self, analyzer):
        """Test improvement suggestion generation"""
        poor_prompt = "fix the thing"
        analysis = analyzer.analyze(poor_prompt)

        assert len(analysis.improvements) > 0
        assert any("clarity" in imp.get("category", "") for imp in analysis.improvements)

    def test_strength_identification(self, analyzer):
        """Test strength detection"""
        good_prompt = "Update the user authentication module in auth.py to handle OAuth 2.0"
        analysis = analyzer.analyze(good_prompt)

        assert len(analysis.strengths) > 0

    def test_feedback_generation(self, analyzer):
        """Test human-readable feedback generation"""
        prompt = "debug the application"
        analysis = analyzer.analyze(prompt)
        feedback = analyzer.generate_feedback(analysis)

        assert isinstance(feedback, str)
        assert "Score" in feedback
        assert "Clarity" in feedback

    def test_skill_level_determination(self, analyzer):
        """Test skill level categorization"""
        assert analyzer._get_skill_level(95) == "Expert"
        assert analyzer._get_skill_level(80) == "Advanced"
        assert analyzer._get_skill_level(65) == "Intermediate"
        assert analyzer._get_skill_level(45) == "Developing"
        assert analyzer._get_skill_level(30) == "Beginner"

    def test_learning_persistence(self, analyzer, tmp_path):
        """Test learning data persistence"""
        prompt = "test prompt for persistence"
        analyzer.analyze(prompt)

        # Check if analysis was saved
        saved_files = list((tmp_path / "learning").glob("analysis_*.json"))
        assert len(saved_files) == 1

    def test_no_emojis_in_output(self, analyzer):
        """Test P10 compliance - no emojis in output"""
        prompt = "simple test prompt"
        analysis = analyzer.analyze(prompt)
        feedback = analyzer.generate_feedback(analysis)

        # Check for common emojis (should not be present)
        emoji_chars = ["✅", "❌", "⚠️", "💡", "📚", "🎯"]
        for emoji in emoji_chars:
            assert emoji not in feedback

    def test_edge_cases(self, analyzer):
        """Test edge cases"""
        # Empty prompt
        empty_analysis = analyzer.analyze("")
        assert empty_analysis.overall_score >= 0

        # Very long prompt
        long_prompt = " ".join(["word"] * 500)
        long_analysis = analyzer.analyze(long_prompt)
        assert long_analysis.word_count == 500

        # Special characters
        special_prompt = "Fix the bug in function_name() -> Result<T, E>"
        special_analysis = analyzer.analyze(special_prompt)
        assert special_analysis is not None

    @pytest.mark.parametrize(
        "prompt,expected_task",
        [
            ("do something with the code", "general"),
            ("fix the authentication bug", "debugging"),
            ("analyze the code structure", "analysis"),
            ("test the login feature", "testing"),
            ("design the dashboard interface", "ui_development"),
        ],
    )
    def test_task_type_detection(self, prompt, expected_task):
        """Test task type detection with various prompts"""
        from prompt_mcp_advisor import PromptMCPAdvisor

        advisor = PromptMCPAdvisor()
        detected = advisor._detect_task_type(prompt)
        assert detected == expected_task


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
