"""
Integration tests for EnhancedTaskExecutor v1.1.0
Tests all 4 Trust Score 8.0+ patterns working together
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestEnhancedExecutorIntegration:
    """Test v1.1.0 integration with all 4 patterns"""

    def test_executor_initialization(self):
        """Test: Executor initializes with all v1.1.0 components"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)

        # Verify v1.1.0 components exist
        assert hasattr(executor, "project_steering")
        assert hasattr(executor, "evidence_tracker")
        assert hasattr(executor, "context_loader")

    def test_project_steering_integration(self):
        """Test: Project steering generates context automatically"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create minimal project structure
            (temp_dir / "requirements.txt").write_text("pytest==8.0.0\n")
            (temp_dir / "scripts").mkdir()

            # Change to temp directory
            import os

            old_cwd = os.getcwd()
            os.chdir(temp_dir)

            # Generate project context
            executor.project_steering.generate(dry_run=False)

            # Verify dev-context/ created
            assert (temp_dir / "dev-context").exists()
            assert (temp_dir / "dev-context" / "tech.md").exists()
            assert (temp_dir / "dev-context" / "structure.md").exists()

            os.chdir(old_cwd)

        finally:
            shutil.rmtree(temp_dir)

    def test_evidence_tracker_integration(self):
        """Test: Evidence tracker collects data automatically"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)

        # Track fake task execution
        with executor.evidence_tracker.track_task_execution("T1", "Test task"):
            pass

        # Verify evidence collected
        assert len(executor.evidence_tracker.events) == 1
        event = executor.evidence_tracker.events[0]
        assert event["task_id"] == "T1"
        assert event["status"] == "SUCCESS"
        assert "duration" in event
        assert "memory_delta" in event

    def test_evidence_report_generation(self):
        """Test: Evidence tracker generates comprehensive report"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)

        # Execute multiple tasks
        for i in range(3):
            with executor.evidence_tracker.track_task_execution(f"T{i+1}", f"Task {i+1}"):
                pass

        # Generate report
        report = executor.evidence_tracker.generate_report()

        assert report["total_tasks"] == 3
        assert report["success_rate"] == 1.0
        assert "avg_duration" in report
        assert "total_duration" in report

    def test_context_loader_integration(self):
        """Test: Context loader analyzes project and recommends articles"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create API project structure
            (temp_dir / "tests").mkdir()
            (temp_dir / "app").mkdir()
            (temp_dir / "app" / "routers").mkdir()

            # Analyze context
            recommendations = executor.context_loader.recommend_articles(temp_dir, "Add API endpoint")

            # Verify recommendations
            assert "Article V (Emoji)" in recommendations  # Always enforced
            assert "Article III (TDD)" in recommendations or "Article VII (API)" in recommendations

        finally:
            shutil.rmtree(temp_dir)

    def test_full_integration_workflow(self):
        """Test: Full v1.1.0 workflow with all components"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor
        from scripts.constitutional_guards import ConstitutionalGuard, Task as GuardTask

        executor = EnhancedTaskExecutor(verbose=False)

        # 1. Project Steering (should not fail)
        executor.project_steering  # Component exists

        # 2. Guard Validation
        tasks = [
            GuardTask(id="T1", description="Write test", phase=1, order=1, type="test"),
            GuardTask(id="T2", description="Implement feature", phase=1, order=2, type="implementation"),
        ]
        guard_result = ConstitutionalGuard.against_implementation_before_tests(tasks)
        assert guard_result.succeeded is True

        # 3. Evidence Tracking
        with executor.evidence_tracker.track_task_execution("T1", "Integration test"):
            pass

        # 4. Context-Aware Loading
        recommendations = executor.context_loader.recommend_articles(Path("."), "Integration test")
        assert "Article V (Emoji)" in recommendations

        # Verify all components worked
        assert len(executor.evidence_tracker.events) == 1
        assert executor.evidence_tracker.events[0]["status"] == "SUCCESS"


class TestEnhancedExecutorPerformance:
    """Test v1.1.0 performance improvements"""

    def test_evidence_collection_overhead(self):
        """Test: Evidence collection adds minimal overhead (<1ms)"""
        import time
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)

        # Measure overhead
        start = time.time()
        with executor.evidence_tracker.track_task_execution("T1", "Performance test"):
            pass  # No actual work
        duration = time.time() - start

        # Overhead should be minimal
        assert duration < 0.01  # <10ms acceptable

    def test_context_analysis_speed(self):
        """Test: Context analysis completes quickly (<100ms)"""
        import time
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)
        temp_dir = Path(tempfile.mkdtemp())

        try:
            (temp_dir / "tests").mkdir()
            (temp_dir / "app").mkdir()

            start = time.time()
            executor.context_loader.analyze_project_context(temp_dir, "Add feature")
            duration = time.time() - start

            assert duration < 0.1  # <100ms

        finally:
            shutil.rmtree(temp_dir)


class TestEnhancedExecutorErrorHandling:
    """Test v1.1.0 error handling and edge cases"""

    def test_failed_task_evidence_collection(self):
        """Test: Evidence collected even when task fails"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)

        # Execute failing task
        with pytest.raises(ValueError):
            with executor.evidence_tracker.track_task_execution("T1", "Failing task"):
                raise ValueError("Intentional test failure")

        # Evidence still collected
        assert len(executor.evidence_tracker.events) == 1
        event = executor.evidence_tracker.events[0]
        assert event["status"] == "FAILED"
        assert "error" in event
        assert "ValueError" in event["error"]

    def test_missing_project_structure(self):
        """Test: Graceful handling of missing project files"""
        from scripts.enhanced_task_executor import EnhancedTaskExecutor

        executor = EnhancedTaskExecutor(verbose=False)
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Empty directory
            recommendations = executor.context_loader.recommend_articles(temp_dir, "Simple task")

            # Should still work with minimal recommendations
            assert "Article V (Emoji)" in recommendations  # Always enforced

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
