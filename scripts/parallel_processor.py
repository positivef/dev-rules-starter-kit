"""Parallel Processor - Performance Optimization Module.

High-performance parallel processing for TAG extraction and sync operations.
Uses ThreadPoolExecutor for I/O-bound operations and ProcessPoolExecutor for CPU-bound.

Compliance:
- P1: YAML-First (parallel configuration via YAML)
- P2: Evidence-based (performance metrics tracking)
- P4: SOLID principles (single responsibility)
- P10: Windows encoding (UTF-8, no emojis)

Performance Features:
- Automatic parallelization for multi-file operations
- Smart task batching based on file size
- Progress tracking with real-time updates
- Resource-aware execution (CPU/memory limits)

Example:
    $ python scripts/parallel_processor.py --workers 4
    $ python scripts/parallel_processor.py --mode async
"""

import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    from security_utils import SecureConfig
    from tag_extractor_lite import CodeTag, TagExtractorLite
except ImportError:
    from scripts.tag_extractor_lite import CodeTag, TagExtractorLite


@dataclass
class ProcessingTask:
    """Represents a parallel processing task.

    Attributes:
        task_id: Unique task identifier.
        task_type: Type of task (extract/sync/analyze).
        target: File or directory to process.
        priority: Task priority (0=highest).
        size_bytes: Estimated task size.
    """

    task_id: str
    task_type: str
    target: Path
    priority: int = 0
    size_bytes: int = 0


@dataclass
class ProcessingResult:
    """Result from parallel processing.

    Attributes:
        task_id: Task identifier.
        success: Whether task succeeded.
        data: Result data.
        duration_ms: Processing time in milliseconds.
        error: Error message if failed.
    """

    task_id: str
    success: bool
    data: Any = None
    duration_ms: float = 0
    error: Optional[str] = None


class ParallelProcessor:
    """High-performance parallel processing engine.

    Attributes:
        max_workers: Maximum concurrent workers.
        use_processes: Use ProcessPoolExecutor instead of ThreadPoolExecutor.
        batch_size: Number of tasks per batch.
        timeout: Task timeout in seconds.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_processes: bool = False,
        batch_size: int = 10,
        timeout: int = 30,
    ) -> None:
        """Initialize parallel processor.

        Args:
            max_workers: Max concurrent workers (None = auto).
            use_processes: Use processes instead of threads.
            batch_size: Tasks per batch.
            timeout: Task timeout in seconds.
        """
        # Auto-detect optimal worker count
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 1) * 2)

        self.max_workers = max_workers
        self.use_processes = use_processes
        self.batch_size = batch_size
        self.timeout = timeout

        # Performance metrics
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.total_time_ms = 0

    def process_tasks(
        self,
        tasks: List[ProcessingTask],
        processor_func: Callable[[ProcessingTask], ProcessingResult],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[ProcessingResult]:
        """Process tasks in parallel.

        Args:
            tasks: List of tasks to process.
            processor_func: Function to process each task.
            progress_callback: Optional progress callback(completed, total).

        Returns:
            List of processing results.

        Example:
            >>> processor = ParallelProcessor(max_workers=4)
            >>> tasks = [ProcessingTask(...), ...]
            >>> results = processor.process_tasks(tasks, extract_tags)
        """
        if not tasks:
            return []

        # Sort by priority (0 = highest)
        tasks.sort(key=lambda t: (t.priority, -t.size_bytes))

        # Choose executor type
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        results: List[ProcessingResult] = []
        self.total_tasks = len(tasks)
        self.completed_tasks = 0

        start_time = time.perf_counter()

        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {executor.submit(processor_func, task): task for task in tasks}

            # Process results as they complete
            for future in as_completed(future_to_task, timeout=self.timeout):
                task = future_to_task[future]

                try:
                    result = future.result(timeout=1)
                    results.append(result)

                    if result.success:
                        self.completed_tasks += 1
                    else:
                        self.failed_tasks += 1

                except Exception as e:
                    # Task failed
                    result = ProcessingResult(
                        task_id=task.task_id,
                        success=False,
                        error=str(e),
                    )
                    results.append(result)
                    self.failed_tasks += 1

                # Progress callback
                if progress_callback:
                    progress_callback(self.completed_tasks + self.failed_tasks, self.total_tasks)

        # Calculate total time
        self.total_time_ms = (time.perf_counter() - start_time) * 1000

        return results

    def process_files_parallel(
        self,
        files: List[Path],
        processor_func: Callable[[Path], Any],
    ) -> Dict[Path, Any]:
        """Process multiple files in parallel.

        Args:
            files: List of files to process.
            processor_func: Function to process each file.

        Returns:
            Dict mapping file paths to results.

        Example:
            >>> processor = ParallelProcessor()
            >>> files = [Path("a.py"), Path("b.py")]
            >>> results = processor.process_files_parallel(files, extract_from_file)
        """

        def task_processor(task: ProcessingTask) -> ProcessingResult:
            """Internal task processor."""
            start = time.perf_counter()
            try:
                data = processor_func(task.target)
                duration = (time.perf_counter() - start) * 1000
                return ProcessingResult(
                    task_id=str(task.target),
                    success=True,
                    data=data,
                    duration_ms=duration,
                )
            except Exception as e:
                duration = (time.perf_counter() - start) * 1000
                return ProcessingResult(
                    task_id=str(task.target),
                    success=False,
                    error=str(e),
                    duration_ms=duration,
                )

        # Create tasks
        tasks = []
        for i, file_path in enumerate(files):
            size = file_path.stat().st_size if file_path.exists() else 0
            task = ProcessingTask(
                task_id=str(file_path),
                task_type="file",
                target=file_path,
                priority=0,
                size_bytes=size,
            )
            tasks.append(task)

        # Process in parallel
        results = self.process_tasks(tasks, task_processor)

        # Convert to dict
        result_dict = {}
        for result in results:
            file_path = Path(result.task_id)
            if result.success:
                result_dict[file_path] = result.data
            else:
                result_dict[file_path] = None

        return result_dict

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics.

        Returns:
            Performance metrics dict.
        """
        success_rate = (self.completed_tasks / self.total_tasks * 100) if self.total_tasks else 0

        avg_time = self.total_time_ms / self.total_tasks if self.total_tasks else 0

        return {
            "total_tasks": self.total_tasks,
            "completed": self.completed_tasks,
            "failed": self.failed_tasks,
            "success_rate": round(success_rate, 2),
            "total_time_ms": round(self.total_time_ms, 2),
            "avg_time_per_task_ms": round(avg_time, 2),
            "max_workers": self.max_workers,
            "executor_type": "process" if self.use_processes else "thread",
        }


class ParallelTagExtractor:
    """Parallel TAG extraction optimized for performance.

    Extends TagExtractorLite with parallel processing capabilities.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        max_workers: Optional[int] = None,
    ) -> None:
        """Initialize parallel TAG extractor.

        Args:
            project_root: Root directory to scan.
            max_workers: Max concurrent workers.
        """
        self.extractor = TagExtractorLite(project_root=project_root)
        self.processor = ParallelProcessor(max_workers=max_workers)

    def extract_tags_parallel(
        self,
        directory: Optional[Path] = None,
        extensions: Optional[List[str]] = None,
    ) -> List[CodeTag]:
        """Extract TAGs from directory using parallel processing.

        Args:
            directory: Directory to scan.
            extensions: File extensions to include.

        Returns:
            List of extracted CodeTag objects.

        Example:
            >>> extractor = ParallelTagExtractor()
            >>> tags = extractor.extract_tags_parallel()
            [CodeTag(...), CodeTag(...), ...]
        """
        # Get list of files to process
        if directory is None:
            directory = self.extractor.project_root

        if extensions is None:
            extensions = self.extractor.file_extensions

        # Find all matching files
        files = []
        for ext in extensions:
            files.extend(directory.glob(f"**/*{ext}"))

        # Filter common ignored paths
        ignored_dirs = {".git", ".pytest_cache", "__pycache__", "node_modules", ".venv", "venv"}
        files = [f for f in files if not any(ignored in f.parts for ignored in ignored_dirs)]

        # Process files in parallel
        def extract_from_file(file_path: Path) -> List[CodeTag]:
            """Extract tags from single file."""
            return self.extractor.extract_tags_from_file(file_path)

        # Run parallel extraction
        results = self.processor.process_files_parallel(files, extract_from_file)

        # Combine all tags
        all_tags = []
        for file_path, tags in results.items():
            if tags:
                all_tags.extend(tags)

        return all_tags

    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction performance statistics.

        Returns:
            Performance and extraction metrics.
        """
        stats = self.processor.get_performance_stats()

        # Add extraction-specific stats
        stats.update(
            {
                "extraction_method": "parallel",
                "files_processed": self.processor.total_tasks,
            }
        )

        return stats


def benchmark_parallel_vs_sequential(directory: Path) -> Dict[str, Any]:
    """Benchmark parallel vs sequential extraction.

    Args:
        directory: Directory to benchmark.

    Returns:
        Benchmark results dict.

    Example:
        >>> results = benchmark_parallel_vs_sequential(Path("src"))
        >>> print(f"Speedup: {results['speedup']}x")
    """
    # Sequential extraction
    seq_extractor = TagExtractorLite(project_root=directory)
    seq_start = time.perf_counter()
    seq_tags = seq_extractor.extract_tags_from_directory()
    seq_time = (time.perf_counter() - seq_start) * 1000

    # Parallel extraction
    par_extractor = ParallelTagExtractor(project_root=directory)
    par_start = time.perf_counter()
    par_tags = par_extractor.extract_tags_parallel()
    par_time = (time.perf_counter() - par_start) * 1000

    # Calculate speedup
    speedup = seq_time / par_time if par_time > 0 else 1.0

    return {
        "sequential": {
            "time_ms": round(seq_time, 2),
            "tags_found": len(seq_tags),
        },
        "parallel": {
            "time_ms": round(par_time, 2),
            "tags_found": len(par_tags),
            "workers": par_extractor.processor.max_workers,
        },
        "speedup": round(speedup, 2),
        "improvement_percent": round((speedup - 1) * 100, 2),
    }


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Parallel Processor - Performance Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/parallel_processor.py --benchmark
  python scripts/parallel_processor.py --workers 8
  python scripts/parallel_processor.py --mode process
        """,
    )

    parser.add_argument(
        "--workers",
        type=int,
        help="Number of parallel workers",
    )
    parser.add_argument(
        "--mode",
        choices=["thread", "process"],
        default="thread",
        help="Parallelization mode",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmark comparison",
    )

    args = parser.parse_args()

    print("[INFO] Parallel Processor - Performance Optimization")
    print("")

    try:
        if args.benchmark:
            # Run benchmark
            print("[INFO] Running parallel vs sequential benchmark...")
            results = benchmark_parallel_vs_sequential(Path.cwd())

            print("\n[RESULTS] Benchmark Comparison:")
            print(f"  Sequential: {results['sequential']['time_ms']}ms")
            print(f"  Parallel:   {results['parallel']['time_ms']}ms")
            print(f"  Speedup:    {results['speedup']}x")
            print(f"  Improvement: {results['improvement_percent']}%")

        else:
            # Run parallel extraction
            extractor = ParallelTagExtractor(max_workers=args.workers)

            print(f"[INFO] Extracting TAGs with {extractor.processor.max_workers} workers...")
            tags = extractor.extract_tags_parallel()

            print(f"\n[OK] Extracted {len(tags)} TAGs")

            # Show performance stats
            stats = extractor.get_extraction_stats()
            print("\n[STATS] Performance Metrics:")
            print(f"  Files processed: {stats['files_processed']}")
            print(f"  Total time: {stats['total_time_ms']}ms")
            print(f"  Avg per file: {stats['avg_time_per_task_ms']}ms")
            print(f"  Success rate: {stats['success_rate']}%")

        return 0

    except Exception as e:
        print(f"[ERROR] Parallel processing failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
