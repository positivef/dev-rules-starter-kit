#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Prompt MCP Advisor - P8 (Test First) Compliance

Tests cover:
- MCP server recommendations
- Skill recommendations
- Parallel opportunity detection
- Inefficiency detection
- Performance estimation
"""

import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_mcp_advisor import PromptMCPAdvisor


class TestPromptMCPAdvisor:
    """Test suite for PromptMCPAdvisor"""

    @pytest.fixture
    def advisor(self, tmp_path):
        """Create advisor instance"""
        return PromptMCPAdvisor(learning_dir=tmp_path / "mcp_advice")

    def test_initialization(self, advisor):
        """Test advisor initialization"""
        assert advisor is not None
        assert advisor.learning_dir.exists()

    def test_task_type_detection(self, advisor):
        """Test task type detection"""
        assert advisor._detect_task_type("debug the error") == "debugging"
        assert advisor._detect_task_type("analyze the code") == "analysis"
        assert advisor._detect_task_type("implement the feature") == "coding"
        assert advisor._detect_task_type("refactor the module") == "refactoring"
        assert advisor._detect_task_type("test the component") == "testing"
        assert advisor._detect_task_type("design button interface") == "ui_development"
        assert advisor._detect_task_type("document the API") == "documentation"
        assert advisor._detect_task_type("process CSV data") == "data_processing"

    def test_mcp_server_recommendations(self, advisor):
        """Test MCP server recommendation logic"""
        # Sequential for debugging
        debug_prompt = "debug why the API is slow and investigate the root cause"
        debug_analysis = advisor.analyze(debug_prompt)
        mcp_names = [r.server_name for r in debug_analysis.mcp_recommendations]
        assert "sequential" in mcp_names

        # Context7 for framework
        framework_prompt = "import React hooks and implement useState pattern"
        framework_analysis = advisor.analyze(framework_prompt)
        mcp_names = [r.server_name for r in framework_analysis.mcp_recommendations]
        assert "context7" in mcp_names

        # Morphllm for bulk operations
        bulk_prompt = "refactor all files to update the naming convention"
        bulk_analysis = advisor.analyze(bulk_prompt)
        mcp_names = [r.server_name for r in bulk_analysis.mcp_recommendations]
        assert "morphllm" in mcp_names

    def test_skill_recommendations(self, advisor):
        """Test skill recommendation logic"""
        # PDF skill
        pdf_prompt = "extract tables from the PDF report and fill the form"
        pdf_analysis = advisor.analyze(pdf_prompt)
        skill_names = [r.skill_name for r in pdf_analysis.skill_recommendations]
        assert "pdf" in skill_names

        # Excel skill
        excel_prompt = "create Excel spreadsheet with formulas and pivot tables"
        excel_analysis = advisor.analyze(excel_prompt)
        skill_names = [r.skill_name for r in excel_analysis.skill_recommendations]
        assert "xlsx" in skill_names

    def test_parallel_opportunity_detection(self, advisor):
        """Test detection of parallelization opportunities"""
        # Multiple files
        multi_prompt = "process multiple files and update all configurations"
        multi_analysis = advisor.analyze(multi_prompt)
        assert len(multi_analysis.parallel_opportunities) > 0

        # Numbered list
        numbered_prompt = """1. Analyze the code
        2. Run the tests
        3. Generate report
        4. Send email"""
        numbered_analysis = advisor.analyze(numbered_prompt)
        assert any("numbered steps" in opp for opp in numbered_analysis.parallel_opportunities)

    def test_inefficiency_detection(self, advisor):
        """Test inefficiency detection"""
        # Sequential processing
        sequential_prompt = "check each file one by one for errors"
        seq_analysis = advisor.analyze(sequential_prompt)
        assert any("Sequential processing" in ineff for ineff in seq_analysis.inefficiencies)

        # Missing context
        vague_prompt = "analyze the complex system architecture and find issues"
        vague_analysis = advisor.analyze(vague_prompt)
        assert len(vague_analysis.inefficiencies) > 0

    def test_confidence_scoring(self, advisor):
        """Test confidence calculation for recommendations"""
        # High confidence (multiple triggers)
        strong_prompt = "debug the error, analyze the issue, investigate why it fails"
        strong_analysis = advisor.analyze(strong_prompt)
        if strong_analysis.mcp_recommendations:
            assert strong_analysis.mcp_recommendations[0].confidence > 0.5

        # Low confidence (single trigger)
        weak_prompt = "check the code"
        weak_analysis = advisor.analyze(weak_prompt)
        # May not have recommendations
        assert weak_analysis is not None

    def test_advice_generation(self, advisor):
        """Test human-readable advice generation"""
        prompt = "refactor React components to use hooks"
        analysis = advisor.analyze(prompt)
        advice = advisor.generate_advice(analysis)

        assert isinstance(advice, str)
        assert "Tool Selection Advice" in advice

    def test_performance_estimation(self, advisor):
        """Test time savings estimation"""
        # Morphllm optimization
        morph_prompt = "bulk update all TypeScript interfaces"
        morph_analysis = advisor.analyze(morph_prompt)
        assert morph_analysis.estimated_time_savings != "baseline"

        # Parallel opportunities
        parallel_prompt = "test all modules and generate reports for each"
        parallel_analysis = advisor.analyze(parallel_prompt)
        # Should detect parallel opportunities
        assert len(parallel_analysis.parallel_opportunities) > 0

    def test_data_persistence(self, advisor, tmp_path):
        """Test analysis persistence"""
        prompt = "test MCP advisor persistence"
        advisor.analyze(prompt)

        # Check saved file
        saved_files = list((tmp_path / "mcp_advice").glob("analysis_*.json"))
        assert len(saved_files) == 1

    def test_alternative_recommendations(self, advisor):
        """Test alternative MCP server suggestions"""
        prompt = "rename function across multiple files"
        analysis = advisor.analyze(prompt)

        # Should recommend either morphllm or serena
        mcp_names = [r.server_name for r in analysis.mcp_recommendations]
        assert "morphllm" in mcp_names or "serena" in mcp_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
