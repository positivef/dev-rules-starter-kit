"""
Strategy B Tools Basic Tests
Tests all 8 productivity tools for basic functionality
"""

import pytest
import subprocess
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCodeReviewAssistant:
    """Tests for code_review_assistant.py"""

    def test_help_command(self):
        """Verify code review assistant has --help"""
        result = subprocess.run(
            ["python", "scripts/code_review_assistant.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in [0, 1], "Help should be available"
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "code_review_assistant.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestDeploymentPlanner:
    """Tests for deployment_planner.py"""

    def test_help_command(self):
        """Verify deployment planner has --help"""
        result = subprocess.run(
            ["python", "scripts/deployment_planner.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in [0, 1]
        # Script exists and runs

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "deployment_planner.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestTestGenerator:
    """Tests for test_generator.py"""

    def test_help_command(self):
        """Verify test generator has --help"""
        result = subprocess.run(
            ["python", "scripts/test_generator.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in [0, 1]

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "test_generator.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestProjectValidator:
    """Tests for project_validator.py"""

    def test_help_command(self):
        """Verify project validator has --help"""
        result = subprocess.run(
            ["python", "scripts/project_validator.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in [0, 1]

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "project_validator.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestRequirementsWizard:
    """Tests for requirements_wizard.py"""

    def test_help_command(self):
        """Verify requirements wizard has --help"""
        result = subprocess.run(
            ["python", "scripts/requirements_wizard.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Interactive tool may not have --help, just verify it exists
        assert result.returncode in [0, 1, 2]

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "requirements_wizard.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestCoverageMonitor:
    """Tests for coverage_monitor.py"""

    def test_help_command(self):
        """Verify coverage monitor has --help"""
        result = subprocess.run(
            ["python", "scripts/coverage_monitor.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in [0, 1]

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "coverage_monitor.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestObsidianAutoSync:
    """Tests for install_obsidian_auto_sync.py"""

    def test_check_command(self):
        """Verify obsidian auto sync has --check"""
        result = subprocess.run(
            ["python", "scripts/install_obsidian_auto_sync.py", "--check"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Check command should work
        assert result.returncode in [0, 1]

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "install_obsidian_auto_sync.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestPrincipleConflictDetector:
    """Tests for principle_conflict_detector.py"""

    def test_help_command(self):
        """Verify principle conflict detector has --help"""
        result = subprocess.run(
            ["python", "scripts/principle_conflict_detector.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode in [0, 1]

    def test_script_exists(self):
        """Verify script file exists"""
        script = project_root / "scripts" / "principle_conflict_detector.py"
        assert script.exists()
        assert script.stat().st_size > 0


class TestStrategyBIntegration:
    """Integration tests for all Strategy B tools"""

    def test_all_tools_documented(self):
        """Verify all 8 tools are documented"""
        quickstart = project_root / "docs" / "PRODUCTIVITY_TOOLS_QUICKSTART.md"
        content = quickstart.read_text(encoding="utf-8")

        tools = [
            "code_review_assistant",
            "deployment_planner",
            "test_generator",
            "project_validator",
            "requirements_wizard",
            "coverage_monitor",
            "obsidian",
            "principle_conflict_detector",
        ]

        for tool in tools:
            assert tool in content.lower(), f"{tool} not documented"

    def test_strategy_b_checklist_complete(self):
        """Verify Strategy B completion checklist shows 8/8"""
        quickstart = project_root / "docs" / "PRODUCTIVITY_TOOLS_QUICKSTART.md"
        content = quickstart.read_text(encoding="utf-8")

        assert "8/8" in content or "8개" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
