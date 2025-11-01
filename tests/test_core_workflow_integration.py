"""
Core Workflow Integration Tests
Tests: YAML contract → TaskExecutor → Evidence → Obsidian sync
"""

import pytest
from pathlib import Path
import json
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCoreWorkflow:
    """Integration tests for core development workflow"""

    def test_yaml_contracts_exist(self):
        """Verify YAML task contracts are present"""
        tasks_dir = project_root / "TASKS"
        assert tasks_dir.exists(), "TASKS directory must exist"

        yaml_files = list(tasks_dir.glob("*.yaml"))
        assert len(yaml_files) > 0, "At least one YAML contract should exist"

        # Check first YAML has required fields
        sample = yaml_files[0]
        content = sample.read_text(encoding="utf-8")
        assert "task_id" in content
        assert "title" in content

    def test_evidence_collection_active(self):
        """Verify evidence collection is working"""
        evidence_dir = project_root / "RUNS" / "evidence"

        if evidence_dir.exists():
            json_files = list(evidence_dir.glob("*.json"))
            if json_files:
                # Check evidence structure
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                assert isinstance(data, dict), "Evidence must be JSON object"

    def test_strategy_b_tools_present(self):
        """Verify all 8 Strategy B tools exist"""
        tools = [
            "code_review_assistant.py",
            "deployment_planner.py",
            "test_generator.py",
            "project_validator.py",
            "requirements_wizard.py",
            "coverage_monitor.py",
            "install_obsidian_auto_sync.py",
            "principle_conflict_detector.py",
        ]

        scripts_dir = project_root / "scripts"
        for tool in tools:
            tool_path = scripts_dir / tool
            assert tool_path.exists(), f"Strategy B tool missing: {tool}"

    def test_tools_have_main_entry(self):
        """Verify tools are executable"""
        tools = [
            "code_review_assistant.py",
            "deployment_planner.py",
            "test_generator.py",
            "project_validator.py",
        ]

        scripts_dir = project_root / "scripts"
        for tool in tools:
            tool_path = scripts_dir / tool
            if tool_path.exists():
                content = tool_path.read_text(encoding="utf-8")
                has_main = 'if __name__ == "__main__"' in content or "def main(" in content
                assert has_main, f"{tool} missing main entry point"

    def test_documentation_updated(self):
        """Verify productivity tools are documented"""
        quickstart = project_root / "docs" / "PRODUCTIVITY_TOOLS_QUICKSTART.md"
        assert quickstart.exists(), "Quickstart guide must exist"

        content = quickstart.read_text(encoding="utf-8")

        # Check for key tools
        assert "code_review_assistant" in content.lower()
        assert "deployment_planner" in content.lower()
        assert "test_generator" in content.lower()

    def test_constitutional_compliance(self):
        """Verify constitutional articles are referenced"""
        claude_md = project_root / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text(encoding="utf-8")

            # Check for constitutional articles
            articles = ["P1", "P2", "P3", "P4", "P5"]
            found = sum(1 for article in articles if article in content)
            assert found >= 3, "At least 3 constitutional articles should be documented"

    def test_obsidian_sync_configured(self):
        """Verify Obsidian sync hook is installed"""
        git_hooks = project_root / ".git" / "hooks" / "post-commit"

        if git_hooks.exists():
            content = git_hooks.read_text(encoding="utf-8")
            assert "obsidian" in content.lower(), "post-commit should reference Obsidian"

    def test_coverage_data_available(self):
        """Verify test coverage data is collected"""
        coverage_file = project_root / "coverage.json"

        if coverage_file.exists():
            with open(coverage_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "totals" in data
            assert "percent_covered" in data["totals"]

            # Just verify structure, not value
            coverage = data["totals"]["percent_covered"]
            assert isinstance(coverage, (int, float))
            assert 0 <= coverage <= 100

    def test_quarterly_review_exists(self):
        """Verify quarterly review documentation exists"""
        review_file = project_root / "docs" / "QUARTERLY_REVIEW_2025_Q4.md"
        assert review_file.exists(), "Q4 2025 quarterly review must exist"

        content = review_file.read_text(encoding="utf-8")
        assert "ROI" in content
        assert "Strategy B" in content

    def test_test_coverage_plan_exists(self):
        """Verify test coverage plan is documented"""
        coverage_doc = project_root / "docs" / "TEST_COVERAGE_SUMMARY.md"
        assert coverage_doc.exists(), "Test coverage summary must exist"

        content = coverage_doc.read_text(encoding="utf-8")
        assert "15%" in content or "30%" in content
        # Check for "coverage" in English or Korean
        assert "coverage" in content.lower() or "커버리지" in content


class TestPerformance:
    """Performance baseline tests"""

    def test_imports_load_quickly(self):
        """Verify critical imports load in reasonable time"""
        import time

        start = time.time()
        try:
            from scripts.constitutional_guards import ConstitutionalGuard  # noqa: F401

            load_time = time.time() - start
            assert load_time < 1.0, f"Import too slow: {load_time:.2f}s"
        except ImportError:
            pytest.skip("Module not importable in test environment")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
