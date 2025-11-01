#!/usr/bin/env python3
"""
Progress Tracker for TaskExecutor

Purpose:
- Real-time progress visualization during task execution
- Estimated time remaining calculation
- Step-by-step status updates

Constitutional Compliance:
- [P6] Observability
- [P10] Windows UTF-8 (ASCII-only output)
"""

from typing import Optional, List
from datetime import datetime


class ProgressTracker:
    """Track and display task execution progress"""

    def __init__(self, total_steps: int, task_id: str):
        """
        Initialize progress tracker.

        Args:
            total_steps: Total number of steps to complete
            task_id: Task identifier for display
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.task_id = task_id
        self.start_time = datetime.now()
        self.step_times: List[float] = []
        self.enabled = True  # Can be disabled for testing

    def start_step(self, step_name: str) -> None:
        """
        Start a new step.

        Args:
            step_name: Name of the step being executed
        """
        self.current_step += 1
        self.step_start_time = datetime.now()

        if not self.enabled:
            return

        # Calculate progress percentage
        progress_pct = (self.current_step / self.total_steps) * 100

        # Create progress bar (ASCII-only)
        bar_width = 40
        filled = int(bar_width * self.current_step / self.total_steps)
        bar = "[" + "=" * filled + ">" + " " * (bar_width - filled - 1) + "]"

        # Estimate remaining time
        eta_str = self._calculate_eta()

        # Print progress
        print(f"\n[PROGRESS] {bar} {progress_pct:5.1f}%", flush=True)
        print(f"[STEP {self.current_step}/{self.total_steps}] {step_name}", flush=True)
        if eta_str:
            print(f"[ETA] {eta_str}", flush=True)

    def complete_step(self, success: bool = True) -> None:
        """
        Mark current step as completed.

        Args:
            success: Whether the step completed successfully
        """
        elapsed = (datetime.now() - self.step_start_time).total_seconds()
        self.step_times.append(elapsed)

        if not self.enabled:
            return

        status = "[OK]" if success else "[FAIL]"
        print(f"{status} Completed in {elapsed:.2f}s", flush=True)

    def _calculate_eta(self) -> Optional[str]:
        """Calculate estimated time remaining"""
        if not self.step_times or self.current_step == 0:
            return None

        # Average time per step
        avg_time = sum(self.step_times) / len(self.step_times)

        # Steps remaining
        remaining_steps = self.total_steps - self.current_step

        # Estimated seconds remaining
        eta_seconds = avg_time * remaining_steps

        # Format as human-readable
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s remaining"
        elif eta_seconds < 3600:
            minutes = eta_seconds / 60
            return f"{minutes:.1f}m remaining"
        else:
            hours = eta_seconds / 3600
            return f"{hours:.1f}h remaining"

    def summary(self) -> None:
        """Print execution summary"""
        if not self.enabled:
            return

        total_time = (datetime.now() - self.start_time).total_seconds()
        avg_time = sum(self.step_times) / len(self.step_times) if self.step_times else 0

        print(f"\n[SUMMARY] Task: {self.task_id}")
        print(f"   Total steps: {self.current_step}/{self.total_steps}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average per step: {avg_time:.2f}s")


class SimpleProgressBar:
    """Lightweight progress bar for simple iterations"""

    def __init__(self, total: int, description: str = "", width: int = 40):
        """
        Initialize simple progress bar.

        Args:
            total: Total number of items
            description: Description to show
            width: Width of the progress bar
        """
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.enabled = True

    def update(self, n: int = 1) -> None:
        """
        Update progress.

        Args:
            n: Number of items completed
        """
        self.current += n

        if not self.enabled:
            return

        # Calculate progress
        progress_pct = (self.current / self.total) * 100
        filled = int(self.width * self.current / self.total)
        bar = "=" * filled + ">" + " " * (self.width - filled - 1)

        # Print (with carriage return for same-line update)
        print(
            f"\r{self.description} [{bar}] {self.current}/{self.total} ({progress_pct:.1f}%)",
            end="",
            flush=True,
        )

        # New line when complete
        if self.current >= self.total:
            print()

    def close(self) -> None:
        """Close the progress bar"""
        if self.enabled and self.current < self.total:
            print()  # Ensure we end with a newline


def create_progress_tracker(total_steps: int, task_id: str, enabled: bool = True) -> ProgressTracker:
    """
    Factory function to create progress tracker.

    Args:
        total_steps: Total number of steps
        task_id: Task identifier
        enabled: Whether progress tracking is enabled

    Returns:
        ProgressTracker instance
    """
    tracker = ProgressTracker(total_steps, task_id)
    tracker.enabled = enabled
    return tracker
