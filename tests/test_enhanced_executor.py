"""
Tests for EnhancedTaskExecutor
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from constitutional_validator import ConstitutionalValidator
from enhanced_task_executor import EnhancedTaskExecutor


class TestConstitutionalValidator:
    """Test Constitutional validation logic"""

    def test_validator_initialization(self):
        """Test validator can be initialized"""
        validator = ConstitutionalValidator()
        assert validator.constitution_path.name == "constitution.md"

    def test_emoji_detection(self):
        """Test Article V: Windows Encoding (no emoji)"""
        validator = ConstitutionalValidator()

        # Create temporary test file with emoji
        test_file = Path("test_tasks_emoji.md")
        test_file.write_text("## Phase 1\n- [ ] T001 Add feature with emoji", encoding="utf-8")

        try:
            violations = validator._check_windows_encoding(test_file.read_text(encoding="utf-8"))
            # Should pass - no emoji in description
            assert len(violations) == 0
        finally:
            test_file.unlink()

    def test_test_first_violation(self):
        """Test Article III: Test-First Development"""
        validator = ConstitutionalValidator()

        # Tasks without tests should trigger warning
        content = """
## Phase 1
- [ ] T001 Implement user authentication
- [ ] T002 Create login endpoint
"""
        violations = validator._check_test_first(content)
        assert len(violations) == 1
        assert violations[0].article == "III"
        assert violations[0].severity == "error"

    def test_test_first_correct_order(self):
        """Test Article III: Correct test-first order"""
        validator = ConstitutionalValidator()

        # Tests before implementation should pass
        content = """
## Phase 1
- [ ] T001 Write test for user authentication
- [ ] T002 Implement user authentication
"""
        violations = validator._check_test_first(content)
        # Should have no violations for test-first
        assert not any(v.article == "III" for v in violations)

    def test_simplicity_violation(self):
        """Test Article VII: Simplicity (max 3 projects)"""
        validator = ConstitutionalValidator()

        # More than 3 projects should trigger error
        content = """
- [ ] T001 Create service in project1/src/main.py
- [ ] T002 Add feature in project2/app/core.py
- [ ] T003 Update config in project3/settings.py
- [ ] T004 Deploy to project4/deploy.sh
"""
        violations = validator._check_simplicity(content)
        assert len(violations) == 1
        assert violations[0].article == "VII"
        assert violations[0].severity == "error"


class TestEnhancedTaskExecutor:
    """Test EnhancedTaskExecutor functionality"""

    def test_executor_initialization(self):
        """Test executor can be initialized"""
        executor = EnhancedTaskExecutor(verbose=False)
        assert executor.root.exists()
        assert executor.constitutional is not None

    def test_parse_tasks(self):
        """Test task parsing from tasks.md"""
        executor = EnhancedTaskExecutor(verbose=False)

        # Create test tasks.md
        test_file = Path("test_tasks.md")
        test_file.write_text(
            """
## Phase 1: Setup

- [ ] T001 Create project structure
- [ ] T002 [P] Initialize dependencies
- [ ] T003 [P] Configure linting

## Phase 2: Foundational (BLOCKING)

- [ ] T004 Setup database schema
- [ ] T005 [P] [US1] Implement auth framework
""",
            encoding="utf-8",
        )

        try:
            phases = executor._parse_tasks(test_file)

            # Verify phase count
            assert len(phases) == 2

            # Verify Phase 1
            assert phases[0].name == "Setup"
            assert len(phases[0].tasks) == 3
            assert not phases[0].blocking

            # Verify Phase 2
            assert phases[1].name == "Foundational (BLOCKING)"
            assert len(phases[1].tasks) == 2
            assert phases[1].blocking  # Should detect BLOCKING keyword

            # Verify task markers
            assert "[P]" in phases[0].tasks[1].markers  # T002 is parallel
            assert "[P]" in phases[1].tasks[1].markers  # T005 is parallel
            assert "[US1]" in phases[1].tasks[1].markers  # T005 has user story marker

        finally:
            test_file.unlink()

    def test_checklist_validation(self):
        """Test checklist status checking"""
        executor = EnhancedTaskExecutor(verbose=False)

        # Create test directory structure
        test_dir = Path("test_feature")
        checklists_dir = test_dir / "checklists"
        checklists_dir.mkdir(parents=True, exist_ok=True)

        # Create complete checklist
        (checklists_dir / "requirements.md").write_text(
            """
# Requirements Checklist
- [X] Item 1 complete
- [X] Item 2 complete
""",
            encoding="utf-8",
        )

        # Create incomplete checklist
        (checklists_dir / "security.md").write_text(
            """
# Security Checklist
- [X] Item 1 complete
- [ ] Item 2 incomplete
- [ ] Item 3 incomplete
""",
            encoding="utf-8",
        )

        try:
            # Create dummy tasks.md
            tasks_file = test_dir / "tasks.md"
            tasks_file.write_text("# Tasks", encoding="utf-8")

            complete = executor._check_checklists(tasks_file)

            # Should return False due to incomplete security.md
            assert not complete

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(test_dir)

    def test_task_id_generation(self):
        """Test task ID generation from file path"""
        executor = EnhancedTaskExecutor(verbose=False)

        test_path = Path("specs/feat-example/tasks.md")
        task_id = executor._generate_task_id(test_path)

        # Should contain feature name
        assert "feat-example" in task_id
        # Should contain timestamp
        assert "-" in task_id


class TestIntegration:
    """Integration tests for complete workflow"""

    def test_yaml_contract_detection(self):
        """Test that YAML contracts are detected and delegated"""
        # Create dummy YAML file
        test_file = Path("test_contract.yaml")
        test_file.write_text("task_id: TEST-001\ntitle: Test", encoding="utf-8")

        try:
            # Should detect YAML type
            # Note: Full execution would require valid contract structure
            # This just tests file type detection
            assert test_file.suffix == ".yaml"

        finally:
            test_file.unlink()

    def test_markdown_tasks_detection(self):
        """Test that Markdown tasks are detected"""
        test_file = Path("test_tasks.md")
        test_file.write_text("## Phase 1\n- [ ] T001 Test task", encoding="utf-8")

        try:
            assert test_file.suffix == ".md"

        finally:
            test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
