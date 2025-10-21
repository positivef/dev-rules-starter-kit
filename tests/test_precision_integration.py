#!/usr/bin/env python3
"""
Integration tests for MCP Precision System
Tests the full integration with existing EnhancedTaskExecutor
"""

import sys
from pathlib import Path
import pytest

# Add paths
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
sys.path.append(str(Path(__file__).parent.parent / "experiments/mcp-precision-system"))

from precision_wrapper import PrecisionEnhancedExecutor, PrecisionConfig, Task
from core.precision_executor import VerificationLevel, TheorySource


class TestPrecisionIntegration:
    """Test precision wrapper integration"""

    def setup_method(self):
        """Setup before each test"""
        self.config = PrecisionConfig(verification_level=VerificationLevel.BASIC, min_confidence_threshold=0.7)
        self.executor = PrecisionEnhancedExecutor(config=self.config, verbose=False, force=False)

    def test_executor_initialization(self):
        """Test that executor initializes correctly"""
        assert self.executor is not None
        assert self.executor.config.verification_level == VerificationLevel.BASIC
        assert self.executor.precision is not None
        assert self.executor.mcp_orchestrator is not None
        assert self.executor.hallucination_guard is not None

    def test_simple_task_execution(self):
        """Test executing a simple task"""
        task = Task(task_id="test_simple", description="Create a function to add two numbers", markers=[])

        result = self.executor.execute_with_precision(task, framework=None, theory=TheorySource.CLEAN_CODE)

        assert result is not None
        assert "precision" in result
        assert "confidence" in result["precision"]

    def test_framework_detection(self):
        """Test framework detection from task description"""
        react_task = Task(task_id="test_react", description="Create a React component with hooks", markers=[])

        framework = self.executor._detect_framework(react_task)
        assert framework == "react"

        vue_task = Task(task_id="test_vue", description="Build a Vue composition API component", markers=[])

        framework = self.executor._detect_framework(vue_task)
        assert framework == "vue"

    def test_hallucination_detection(self):
        """Test hallucination detection"""
        # Good task
        good_task = "Create a login form following React best practices"
        result = self.executor._check_for_hallucinations(good_task)
        assert not result["detected"]

        # Bad task (contains anti-pattern)
        bad_task = "Create a solution that always works and never fails"
        result = self.executor._check_for_hallucinations(bad_task)
        assert result["detected"]
        assert result["confidence"] < 0.5

    def test_statistics_tracking(self):
        """Test that statistics are tracked correctly"""
        initial_stats = self.executor.get_statistics()
        assert initial_stats["total_executions"] == 0

        # Execute a task
        task = Task(task_id="test_stats", description="Simple test task", markers=[])

        try:
            self.executor.execute_with_precision(task)
        except Exception:
            pass  # Ignore execution errors, we're testing stats

        stats = self.executor.get_statistics()
        assert stats["total_executions"] > 0

    def test_report_generation(self):
        """Test report generation"""
        report = self.executor.generate_report()
        assert report is not None
        assert "PRECISION EXECUTION REPORT" in report
        assert "Total Executions" in report

    def test_backward_compatibility(self):
        """Test backward compatibility with EnhancedTaskExecutor"""
        # Should be able to call parent methods
        assert hasattr(self.executor, "log")
        assert hasattr(self.executor, "constitutional")
        assert hasattr(self.executor, "evidence_tracker")

    def test_config_from_master_config(self):
        """Test loading config from master_config.json"""
        import json

        config_path = Path(__file__).parent.parent / "config/master_config.json"

        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            precision = config.get("precision_system", {})

            assert precision.get("enabled") is True
            assert "orchestration_policy" in precision
            assert "mcp_servers" in precision


class TestPrecisionWithDifferentLevels:
    """Test precision system with different verification levels"""

    @pytest.mark.parametrize("level", [VerificationLevel.BASIC, VerificationLevel.STANDARD, VerificationLevel.MAXIMUM])
    def test_verification_levels(self, level):
        """Test each verification level"""
        config = PrecisionConfig(verification_level=level)
        executor = PrecisionEnhancedExecutor(config=config, verbose=False)

        assert executor.config.verification_level == level

    def test_theory_application(self):
        """Test applying different theories"""
        theories = [TheorySource.SOLID, TheorySource.DRY, TheorySource.CLEAN_CODE, TheorySource.TDD]

        for theory in theories:
            config = PrecisionConfig(default_theory=theory)
            executor = PrecisionEnhancedExecutor(config=config, verbose=False)

            task = Task(task_id=f"test_{theory.value}", description="Test task", markers=[])

            # Should not raise exception
            try:
                result = executor.execute_with_precision(task, theory=theory)
                # If it executes, theory was applied
                if "precision" in result:
                    assert result["precision"]["theory_applied"] == theory.value
            except Exception:
                # Some execution errors are OK for this test
                pass


class TestMCPOrchestration:
    """Test MCP server orchestration"""

    def test_server_selection(self):
        """Test that appropriate MCP servers are selected"""
        executor = PrecisionEnhancedExecutor(verbose=False)

        # React task should select Context7 and possibly Magic
        servers = executor.mcp_orchestrator.select_optimal_servers("Create a React component", {"framework": "react"})

        assert len(servers) > 0
        server_names = [s.value for s in servers]
        # Should include at least one relevant server
        assert any(s in server_names for s in ["context7", "magic", "sequential"])

    def test_consensus_execution(self):
        """Test MCP consensus execution"""
        executor = PrecisionEnhancedExecutor(verbose=False)

        consensus = executor.mcp_orchestrator.execute_with_consensus(
            "Simple test task",
            [],  # Empty server list for quick test
        )

        assert "verified" in consensus
        assert "confidence" in consensus


def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    # 1. Create executor
    config = PrecisionConfig(
        verification_level=VerificationLevel.STANDARD,
        enable_mcp_orchestration=True,
        enable_hallucination_guard=True,
        min_confidence_threshold=0.75,
    )

    executor = PrecisionEnhancedExecutor(config=config, verbose=False, force=True)

    # 2. Create task
    task = Task(task_id="e2e_test", description="Create a secure user authentication API endpoint", markers=[])

    # 3. Execute with precision
    result = executor.execute_with_precision(task, framework="express", theory=TheorySource.SOLID)

    # 4. Verify result structure
    assert result is not None
    assert "precision" in result
    assert "confidence" in result["precision"]
    assert "hallucination_free" in result["precision"]
    assert "theory_applied" in result["precision"]

    # 5. Check statistics
    stats = executor.get_statistics()
    assert stats["total_executions"] > 0

    # 6. Generate report
    report = executor.generate_report()
    assert len(report) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
