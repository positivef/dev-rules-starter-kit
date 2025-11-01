#!/usr/bin/env python3
"""
Tests for Progress Tracker

Purpose: Verify progress tracking functionality

Constitutional Compliance:
- [P3] Test-First Development
- [P6] Observability
"""

from pathlib import Path
import sys
import io
from contextlib import redirect_stdout

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from progress_tracker import ProgressTracker, SimpleProgressBar, create_progress_tracker


class TestProgressTracker:
    """Test ProgressTracker functionality"""

    def test_initialization(self):
        """Test tracker initialization"""
        tracker = ProgressTracker(total_steps=5, task_id="TEST-01")

        assert tracker.total_steps == 5
        assert tracker.current_step == 0
        assert tracker.task_id == "TEST-01"
        assert tracker.enabled is True

    def test_start_step_increments(self):
        """Test that starting a step increments counter"""
        tracker = ProgressTracker(total_steps=3, task_id="TEST-02")
        tracker.enabled = False  # Disable output for testing

        tracker.start_step("Step 1")
        assert tracker.current_step == 1

        tracker.start_step("Step 2")
        assert tracker.current_step == 2

    def test_complete_step_records_time(self):
        """Test that completing a step records timing"""
        tracker = ProgressTracker(total_steps=2, task_id="TEST-03")
        tracker.enabled = False

        tracker.start_step("Step 1")
        tracker.complete_step(success=True)

        assert len(tracker.step_times) == 1
        assert tracker.step_times[0] >= 0

    def test_disabled_tracker_no_output(self):
        """Test that disabled tracker produces no output"""
        tracker = ProgressTracker(total_steps=2, task_id="TEST-04")
        tracker.enabled = False

        output = io.StringIO()
        with redirect_stdout(output):
            tracker.start_step("Test step")
            tracker.complete_step()
            tracker.summary()

        assert output.getvalue() == ""

    def test_progress_percentage_calculation(self):
        """Test progress percentage is calculated correctly"""
        tracker = ProgressTracker(total_steps=4, task_id="TEST-05")
        tracker.enabled = False

        tracker.start_step("Step 1")
        assert tracker.current_step == 1  # 25%

        tracker.start_step("Step 2")
        assert tracker.current_step == 2  # 50%

        tracker.start_step("Step 3")
        assert tracker.current_step == 3  # 75%

    def test_eta_calculation_with_no_history(self):
        """Test ETA returns None when no history exists"""
        tracker = ProgressTracker(total_steps=3, task_id="TEST-06")

        eta = tracker._calculate_eta()
        assert eta is None

    def test_eta_calculation_with_history(self):
        """Test ETA is calculated based on step history"""
        tracker = ProgressTracker(total_steps=4, task_id="TEST-07")
        tracker.enabled = False

        # Simulate 2 completed steps with 1 second each
        tracker.start_step("Step 1")
        tracker.step_times.append(1.0)
        tracker.complete_step()

        tracker.start_step("Step 2")
        tracker.step_times.append(1.0)
        tracker.complete_step()

        # Should have 2 steps remaining, ~2 seconds
        eta = tracker._calculate_eta()
        assert eta is not None
        assert "s remaining" in eta or "m remaining" in eta


class TestSimpleProgressBar:
    """Test SimpleProgressBar functionality"""

    def test_initialization(self):
        """Test progress bar initialization"""
        bar = SimpleProgressBar(total=10, description="Processing")

        assert bar.total == 10
        assert bar.current == 0
        assert bar.description == "Processing"

    def test_update_increments(self):
        """Test update increments current value"""
        bar = SimpleProgressBar(total=5)
        bar.enabled = False

        bar.update(1)
        assert bar.current == 1

        bar.update(2)
        assert bar.current == 3

    def test_disabled_bar_no_output(self):
        """Test disabled bar produces no output"""
        bar = SimpleProgressBar(total=3)
        bar.enabled = False

        output = io.StringIO()
        with redirect_stdout(output):
            bar.update(1)
            bar.update(1)
            bar.close()

        assert output.getvalue() == ""


class TestCreateProgressTracker:
    """Test factory function"""

    def test_creates_enabled_tracker(self):
        """Test factory creates enabled tracker"""
        tracker = create_progress_tracker(total_steps=3, task_id="TEST-08", enabled=True)

        assert isinstance(tracker, ProgressTracker)
        assert tracker.enabled is True

    def test_creates_disabled_tracker(self):
        """Test factory creates disabled tracker"""
        tracker = create_progress_tracker(total_steps=3, task_id="TEST-09", enabled=False)

        assert isinstance(tracker, ProgressTracker)
        assert tracker.enabled is False


class TestProgressIntegration:
    """Integration tests for realistic scenarios"""

    def test_typical_workflow(self):
        """Test typical task execution workflow"""
        tracker = ProgressTracker(total_steps=3, task_id="WORKFLOW-TEST")
        tracker.enabled = False

        # Step 1
        tracker.start_step("Command: setup")
        assert tracker.current_step == 1
        tracker.complete_step(success=True)
        assert len(tracker.step_times) == 1

        # Step 2
        tracker.start_step("Command: test")
        assert tracker.current_step == 2
        tracker.complete_step(success=True)
        assert len(tracker.step_times) == 2

        # Step 3
        tracker.start_step("Gate: validation")
        assert tracker.current_step == 3
        tracker.complete_step(success=True)
        assert len(tracker.step_times) == 3

        # Should have completed all steps
        assert tracker.current_step == tracker.total_steps

    def test_failed_step_tracking(self):
        """Test tracking when a step fails"""
        tracker = ProgressTracker(total_steps=2, task_id="FAIL-TEST")
        tracker.enabled = False

        tracker.start_step("Command: risky")
        tracker.complete_step(success=False)

        # Should still record the time even on failure
        assert len(tracker.step_times) == 1

    def test_output_contains_ascii_only(self):
        """Test that output uses only ASCII characters (P10 compliance)"""
        tracker = ProgressTracker(total_steps=2, task_id="ASCII-TEST")

        output = io.StringIO()
        with redirect_stdout(output):
            tracker.start_step("Test step")
            tracker.complete_step(success=True)
            tracker.summary()

        output_text = output.getvalue()

        # Check for ASCII-only (no emoji or special unicode)
        assert all(ord(c) < 128 or c in ["\n"] for c in output_text)
        assert "[PROGRESS]" in output_text
        assert "[STEP" in output_text
        assert "[OK]" in output_text or "[FAIL]" in output_text
        assert "[SUMMARY]" in output_text
