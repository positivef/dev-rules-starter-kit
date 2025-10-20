"""
Test Automatic Evidence Tracker (GrowthBook Trust 8.0 pattern)

Based on: /growthbook/growthbook automatic metrics tracking
Pattern: Auto-collect execution evidence without manual intervention
Validation: TDD-first approach
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import time
import json


class TestEvidenceTracker:
    """Test automatic evidence collection during task execution"""

    def test_tracker_initialization(self):
        """Test: EvidenceTracker initializes with empty state"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()
        assert tracker.events == []
        assert tracker.session_start_time is not None

    def test_track_successful_task(self):
        """Test: Track successful task execution"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with tracker.track_task_execution("task-1", "Write unit test"):
            # Simulate task execution
            time.sleep(0.01)

        # Should have 1 event
        assert len(tracker.events) == 1

        # Check event structure
        event = tracker.events[0]
        assert event["task_id"] == "task-1"
        assert event["status"] == "SUCCESS"
        assert event["duration"] > 0
        assert "timestamp" in event
        assert "memory_delta" in event

    def test_track_failed_task(self):
        """Test: Track failed task with exception details"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with pytest.raises(ValueError):
            with tracker.track_task_execution("task-2", "Failing task"):
                raise ValueError("Intentional test failure")

        # Should have 1 event with failure status
        assert len(tracker.events) == 1

        event = tracker.events[0]
        assert event["task_id"] == "task-2"
        assert event["status"] == "FAILED"
        assert "error" in event
        assert "ValueError" in event["error"]
        assert "stack_trace" in event

    def test_track_multiple_tasks(self):
        """Test: Track multiple sequential tasks"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        # Task 1: Success
        with tracker.track_task_execution("task-1", "Task 1"):
            pass

        # Task 2: Success
        with tracker.track_task_execution("task-2", "Task 2"):
            pass

        # Task 3: Fail
        with pytest.raises(RuntimeError):
            with tracker.track_task_execution("task-3", "Task 3"):
                raise RuntimeError("Test error")

        # Should have 3 events
        assert len(tracker.events) == 3
        assert tracker.events[0]["status"] == "SUCCESS"
        assert tracker.events[1]["status"] == "SUCCESS"
        assert tracker.events[2]["status"] == "FAILED"

    def test_automatic_file_tracking(self):
        """Test: Automatically track modified files during execution"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Create test file during task execution
            with tracker.track_task_execution("task-1", "Create file"):
                test_file = temp_dir / "test.txt"
                test_file.write_text("test content")

            event = tracker.events[0]
            assert "files_modified" in event

        finally:
            shutil.rmtree(temp_dir)

    def test_memory_tracking(self):
        """Test: Track memory usage during task execution"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with tracker.track_task_execution("task-1", "Memory test"):
            # Allocate some memory
            _ = [0] * 10000  # Use underscore for unused variable

        event = tracker.events[0]
        assert "memory_delta" in event
        assert isinstance(event["memory_delta"], (int, float))

    def test_duration_tracking(self):
        """Test: Track execution duration accurately"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with tracker.track_task_execution("task-1", "Duration test"):
            time.sleep(0.05)  # 50ms

        event = tracker.events[0]
        assert event["duration"] >= 0.05
        assert event["duration"] < 0.1  # Should not be too long


class TestEvidenceReport:
    """Test evidence report generation"""

    def test_generate_summary_report(self):
        """Test: Generate summary report from collected evidence"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        # Execute 3 tasks
        with tracker.track_task_execution("task-1", "Task 1"):
            time.sleep(0.01)

        with tracker.track_task_execution("task-2", "Task 2"):
            time.sleep(0.01)

        with pytest.raises(RuntimeError):
            with tracker.track_task_execution("task-3", "Task 3"):
                raise RuntimeError("Test error")

        # Generate report
        report = tracker.generate_report()

        assert report["total_tasks"] == 3
        assert report["success_count"] == 2
        assert report["failure_count"] == 1
        assert report["success_rate"] == 2 / 3
        assert "avg_duration" in report
        assert "total_duration" in report

    def test_export_to_json(self):
        """Test: Export evidence to JSON file"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with tracker.track_task_execution("task-1", "Export test"):
            pass

        temp_dir = Path(tempfile.mkdtemp())
        try:
            output_file = temp_dir / "evidence.json"
            tracker.export_to_json(output_file)

            assert output_file.exists()

            # Verify JSON structure
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "events" in data
            assert "summary" in data
            assert len(data["events"]) == 1

        finally:
            shutil.rmtree(temp_dir)

    def test_export_to_obsidian_format(self):
        """Test: Export evidence in Obsidian-compatible markdown"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with tracker.track_task_execution("task-1", "Obsidian test"):
            time.sleep(0.01)

        temp_dir = Path(tempfile.mkdtemp())
        try:
            output_file = temp_dir / "evidence.md"
            tracker.export_to_obsidian(output_file)

            assert output_file.exists()

            content = output_file.read_text(encoding="utf-8")
            assert "# Task Execution Evidence" in content
            assert "task-1" in content
            assert "SUCCESS" in content

        finally:
            shutil.rmtree(temp_dir)


class TestEvidenceMetrics:
    """Test evidence metrics and statistics"""

    def test_calculate_success_rate(self):
        """Test: Calculate task success rate"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        # 7 successes, 3 failures
        for i in range(7):
            with tracker.track_task_execution(f"task-{i}", f"Task {i}"):
                pass

        for i in range(7, 10):
            with pytest.raises(RuntimeError):
                with tracker.track_task_execution(f"task-{i}", f"Task {i}"):
                    raise RuntimeError("Test error")

        report = tracker.generate_report()
        assert report["success_rate"] == 0.7

    def test_calculate_average_duration(self):
        """Test: Calculate average task duration"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        # Execute tasks with known durations
        with tracker.track_task_execution("task-1", "Task 1"):
            time.sleep(0.01)

        with tracker.track_task_execution("task-2", "Task 2"):
            time.sleep(0.02)

        with tracker.track_task_execution("task-3", "Task 3"):
            time.sleep(0.01)

        report = tracker.generate_report()
        avg_duration = report["avg_duration"]

        # Average should be around 0.0133 (0.01 + 0.02 + 0.01) / 3
        assert 0.01 <= avg_duration <= 0.03

    def test_memory_statistics(self):
        """Test: Memory usage statistics"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        with tracker.track_task_execution("task-1", "Memory test"):
            # Allocate memory
            _ = [0] * 100000  # Use underscore for unused variable

        report = tracker.generate_report()
        assert "total_memory_delta" in report


class TestEvidenceIntegration:
    """Test evidence tracker integration with task execution"""

    def test_integration_with_yaml_tasks(self):
        """Test: Evidence tracker works with YAML task execution"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        # Simulate YAML task execution
        tasks = [
            {"id": "1.1", "description": "Write test", "phase": 1},
            {"id": "1.2", "description": "Implement", "phase": 1},
        ]

        for task in tasks:
            with tracker.track_task_execution(task["id"], task["description"]):
                time.sleep(0.001)  # Simulate work

        assert len(tracker.events) == 2
        assert all(e["status"] == "SUCCESS" for e in tracker.events)

    def test_evidence_collection_without_manual_intervention(self):
        """Test: Evidence collected automatically (no manual provenance)"""
        from scripts.automatic_evidence_tracker import AutomaticEvidenceTracker

        tracker = AutomaticEvidenceTracker()

        # User just writes normal code
        with tracker.track_task_execution("task-1", "Normal task"):
            # No manual evidence collection calls needed!
            result = 2 + 2
            assert result == 4

        # Evidence automatically collected
        event = tracker.events[0]
        assert event["task_id"] == "task-1"
        assert event["status"] == "SUCCESS"
        assert "duration" in event
        assert "memory_delta" in event
        assert "timestamp" in event

        # 95% manual work eliminated!


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
