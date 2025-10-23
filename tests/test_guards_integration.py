"""
Integration test for Constitutional Guards with real YAML tasks

Tests guard validation against actual task execution scenarios.
"""

import pytest
from pathlib import Path
import yaml
import sys

# Add project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from scripts.constitutional_guards import (  # noqa: E402
    ConstitutionalGuard,
    Task,
    ConstitutionalViolationError,
    validate_task_list,
)  # noqa: E402


class TestGuardsIntegration:
    """Integration tests for Constitutional Guards with YAML tasks"""

    def test_valid_yaml_task_structure(self):
        """Test: Guards validate correctly structured YAML tasks"""
        yaml_path = Path("TASKS/FEAT-2025-10-20-GUARD-TEST.yaml")

        # Parse YAML
        with open(yaml_path, "r", encoding="utf-8") as f:
            task_data = yaml.safe_load(f)

        # Convert to Task objects
        tasks = []
        for phase_data in task_data["phases"]:
            phase_num = phase_data["phase"]
            for task_item in phase_data["tasks"]:
                task = Task(
                    id=task_item["id"],
                    description=task_item["description"],
                    phase=phase_num,
                    order=task_item["order"],
                    type=task_item["type"],
                )
                tasks.append(task)

        # Validate TDD order
        result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert result.succeeded is True, f"TDD validation failed: {result.message}"

    def test_detect_tdd_violation_in_yaml(self):
        """Test: Guards detect TDD violations in YAML structure"""
        # Create tasks with violation (implementation before test)
        tasks = [
            Task(
                id="1.1",
                description="Implement login without test",
                phase=1,
                order=1,
                type="implementation",
            ),
            Task(id="1.2", description="Write test after implementation", phase=1, order=2, type="test"),
        ]

        result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert result.succeeded is False
        assert "Article III" in result.message
        assert "1.1" in result.message

    def test_validate_task_list_helper(self):
        """Test: validate_task_list() helper function"""
        # Valid task list
        valid_tasks = [
            Task(id="1", description="Write test", phase=1, order=1, type="test"),
            Task(id="2", description="Implement feature", phase=1, order=2, type="implementation"),
        ]

        # Should not raise
        validate_task_list(valid_tasks)

        # Invalid task list
        invalid_tasks = [
            Task(id="1", description="Implement feature", phase=1, order=1, type="implementation"),
            Task(id="2", description="Write test", phase=1, order=2, type="test"),
        ]

        # Should raise ConstitutionalViolationError
        with pytest.raises(ConstitutionalViolationError) as exc_info:
            validate_task_list(invalid_tasks)

        assert "Article III" in str(exc_info.value)

    def test_guard_against_emoji_in_real_files(self):
        """Test: Guards detect emoji in actual project files"""
        # Test against this test file (should pass - no emoji)
        result = ConstitutionalGuard.against_emoji_in_files(Path(__file__))
        assert result.succeeded is True

    def test_guard_against_missing_tests_in_project(self):
        """Test: Guards detect missing tests in project"""
        project_root = Path(".")

        # This project has tests/ directory
        result = ConstitutionalGuard.against_missing_tests(project_root)
        assert result.succeeded is True

    def test_guard_combination_workflow(self):
        """Test: Complete guard workflow for task execution"""
        # Scenario: Pre-execution validation
        tasks = [
            Task(id="1", description="Write unit tests", phase=1, order=1, type="test"),
            Task(id="2", description="Implement feature", phase=1, order=2, type="implementation"),
            Task(id="3", description="Integration test", phase=2, order=1, type="test"),
        ]

        # Step 1: Validate task order (TDD)
        tdd_result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert tdd_result.succeeded is True

        # Step 2: Validate project structure
        project_result = ConstitutionalGuard.against_missing_tests(Path("."))
        assert project_result.succeeded is True

        # Step 3: All guards passed - safe to execute
        print("All guards passed - task execution approved")


class TestGuardPerformance:
    """Test guard performance and efficiency"""

    def test_guard_execution_speed(self):
        """Test: Guards execute quickly (fail-fast principle)"""
        import time

        # Create 100 tasks
        tasks = []
        for i in range(100):
            task_type = "test" if i % 2 == 0 else "implementation"
            tasks.append(Task(id=str(i), description=f"Task {i}", phase=1, order=i, type=task_type))

        start_time = time.time()
        result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        execution_time = time.time() - start_time

        # Should complete in under 10ms
        assert execution_time < 0.01, f"Guard too slow: {execution_time*1000:.2f}ms"
        assert result.succeeded is True

    def test_early_exit_on_first_violation(self):
        """Test: Guards fail fast on first violation"""
        # First task violates TDD
        tasks = [
            Task(id="1", description="Implement", phase=1, order=1, type="implementation"),
            # ... potentially 1000 more tasks
        ]

        result = ConstitutionalGuard.against_implementation_before_tests(tasks)

        # Should detect violation on first task
        assert result.succeeded is False
        assert "1" in result.message


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
