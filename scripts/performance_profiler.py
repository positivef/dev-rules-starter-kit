#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Profiler - Automation Tool Performance Bottleneck Analysis
=======================================================================

Purpose:
1. Measure execution time of existing automation tools
2. Profile memory usage
3. Analyze I/O operations
4. Identify CPU bottlenecks
5. Derive optimization priorities

Measurement Targets:
- auto_improver.py
- auto_test_generator.py
- auto_doc_updater.py
- claude_md_updater.py
- constitutional_validator.py
"""

import time
import psutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys


@dataclass
class PerformanceMetrics:
    """Performance measurement results"""

    tool_name: str
    execution_time: float  # seconds
    memory_peak: float  # MB
    memory_average: float  # MB
    cpu_percent: float
    io_read_bytes: int
    io_write_bytes: int
    success: bool
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Profiling details
    function_calls: int = 0
    top_functions: List[Dict] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class PerformanceProfiler:
    """Performance profiler"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results: List[PerformanceMetrics] = []

        # Output directory
        self.output_dir = self.project_root / "RUNS" / "performance"
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def profile_script(self, script_path: Path, args: List[str] = None, use_profiler: bool = True) -> PerformanceMetrics:
        """
        Execute script and measure performance

        Args:
            script_path: Path to script to measure
            args: Script arguments
            use_profiler: Whether to use cProfile

        Returns:
            PerformanceMetrics object
        """
        print(f"\n[PROFILE] {script_path.name}")
        print("=" * 60)

        args = args or []

        # Process monitoring
        process = None
        memory_samples = []
        cpu_samples = []

        try:
            # Start time
            start_time = time.time()

            # Start process
            cmd = [sys.executable, str(script_path)] + args
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.project_root)

            # Monitor process
            ps_process = psutil.Process(process.pid)
            io_start = ps_process.io_counters()

            while process.poll() is None:
                try:
                    # Memory
                    mem_info = ps_process.memory_info()
                    memory_samples.append(mem_info.rss / 1024 / 1024)  # MB

                    # CPU
                    cpu_samples.append(ps_process.cpu_percent(interval=0.1))

                    time.sleep(0.1)  # 100ms sampling

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break

            # Wait for completion
            stdout, stderr = process.communicate(timeout=300)

            # End time
            end_time = time.time()
            execution_time = end_time - start_time

            # I/O counters
            try:
                io_end = ps_process.io_counters()
                io_read = io_end.read_bytes - io_start.read_bytes
                io_write = io_end.write_bytes - io_start.write_bytes
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                io_read = 0
                io_write = 0

            # Metrics
            metrics = PerformanceMetrics(
                tool_name=script_path.stem,
                execution_time=execution_time,
                memory_peak=max(memory_samples) if memory_samples else 0,
                memory_average=sum(memory_samples) / len(memory_samples) if memory_samples else 0,
                cpu_percent=sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0,
                io_read_bytes=io_read,
                io_write_bytes=io_write,
                success=(process.returncode == 0),
                error_message=stderr.decode("utf-8", errors="ignore") if process.returncode != 0 else None,
            )

            # Print results
            print(f"Execution Time: {execution_time:.3f}s")
            print(f"Memory Peak: {metrics.memory_peak:.2f} MB")
            print(f"Memory Avg: {metrics.memory_average:.2f} MB")
            print(f"CPU Avg: {metrics.cpu_percent:.1f}%")
            print(f"I/O Read: {io_read / 1024 / 1024:.2f} MB")
            print(f"I/O Write: {io_write / 1024 / 1024:.2f} MB")
            print(f"Success: {metrics.success}")

            if not metrics.success:
                print(f"Error: {metrics.error_message[:200]}")

            # Profiling (if enabled and successful)
            if use_profiler and metrics.success:
                print("\n[PROFILING] Running cProfile...")
                prof_metrics = self._run_profiler(script_path, args)
                if prof_metrics:
                    metrics.function_calls = prof_metrics["function_calls"]
                    metrics.top_functions = prof_metrics["top_functions"]

            self.results.append(metrics)
            return metrics

        except subprocess.TimeoutExpired:
            if process:
                process.kill()
            print("[ERROR] Timeout (300s)")
            return PerformanceMetrics(
                tool_name=script_path.stem,
                execution_time=300,
                memory_peak=0,
                memory_average=0,
                cpu_percent=0,
                io_read_bytes=0,
                io_write_bytes=0,
                success=False,
                error_message="Timeout",
            )

        except Exception as e:
            print(f"[ERROR] {e}")
            return PerformanceMetrics(
                tool_name=script_path.stem,
                execution_time=0,
                memory_peak=0,
                memory_average=0,
                cpu_percent=0,
                io_read_bytes=0,
                io_write_bytes=0,
                success=False,
                error_message=str(e),
            )

    def _run_profiler(self, script_path: Path, args: List[str]) -> Optional[Dict]:
        """
        Execute cProfile and analyze

        Returns:
            {
                'function_calls': int,
                'top_functions': [
                    {'function': str, 'cumtime': float, 'calls': int},
                    ...
                ]
            }
        """
        try:
            # Run with profiler
            # NOTE: This re-runs the script, so it's expensive
            # Only use for detailed analysis

            # For now, return None to skip re-execution
            # In production, we'd parse the actual execution profile
            # Would use: prof_output = io.StringIO(), profiler = cProfile.Profile()
            return None

        except Exception as e:
            print(f"[PROFILER ERROR] {e}")
            return None

    def benchmark_all_tools(self):
        """Benchmark all automation tools"""
        print("\n" + "=" * 60)
        print("PERFORMANCE BENCHMARKING - Automation Tools")
        print("=" * 60)

        tools = [
            {
                "script": self.project_root / "scripts" / "auto_improver.py",
                "args": ["--dry-run"],  # Dry run for safety
                "profile": False,  # Too slow to profile
            },
            {"script": self.project_root / "scripts" / "auto_test_generator.py", "args": ["--dry-run"], "profile": False},
            {
                "script": self.project_root / "scripts" / "auto_doc_updater.py",
                "args": ["--dry-run"],
                "profile": True,  # Fast enough to profile
            },
            {"script": self.project_root / "scripts" / "claude_md_updater.py", "args": [], "profile": True},
            {"script": self.project_root / "scripts" / "constitutional_validator.py", "args": [], "profile": True},
        ]

        for tool in tools:
            if not tool["script"].exists():
                print(f"\n[SKIP] {tool['script'].name} (not found)")
                continue

            self.profile_script(tool["script"], args=tool["args"], use_profiler=tool["profile"])

            time.sleep(1)  # Cooldown

    def analyze_bottlenecks(self) -> Dict:
        """
        Analyze bottlenecks

        Returns:
            {
                'slowest_tools': [...],
                'memory_intensive': [...],
                'io_intensive': [...],
                'optimization_priorities': [...]
            }
        """
        if not self.results:
            return {}

        # Sort by execution time
        by_time = sorted(self.results, key=lambda m: m.execution_time, reverse=True)

        # Sort by memory
        by_memory = sorted(self.results, key=lambda m: m.memory_peak, reverse=True)

        # Sort by I/O
        by_io = sorted(self.results, key=lambda m: m.io_read_bytes + m.io_write_bytes, reverse=True)

        # Analysis
        analysis = {
            "slowest_tools": [
                {
                    "tool": m.tool_name,
                    "time": m.execution_time,
                    "potential_speedup": "Parallel processing" if m.execution_time > 2 else "Micro-optimization",
                }
                for m in by_time[:3]
            ],
            "memory_intensive": [
                {
                    "tool": m.tool_name,
                    "peak_mb": m.memory_peak,
                    "avg_mb": m.memory_average,
                    "optimization": "Streaming" if m.memory_peak > 100 else "Caching",
                }
                for m in by_memory[:3]
            ],
            "io_intensive": [
                {
                    "tool": m.tool_name,
                    "read_mb": m.io_read_bytes / 1024 / 1024,
                    "write_mb": m.io_write_bytes / 1024 / 1024,
                    "optimization": "Batch I/O" if (m.io_read_bytes + m.io_write_bytes) > 10 * 1024 * 1024 else "Buffering",
                }
                for m in by_io[:3]
            ],
            "optimization_priorities": [],
        }

        # Priority calculation
        for metric in self.results:
            priority_score = 0
            reasons = []

            # Time weight
            if metric.execution_time > 5:
                priority_score += 3
                reasons.append(f"Long execution time ({metric.execution_time:.1f}s)")
            elif metric.execution_time > 2:
                priority_score += 2
                reasons.append(f"Medium execution time ({metric.execution_time:.1f}s)")

            # Memory weight
            if metric.memory_peak > 200:
                priority_score += 2
                reasons.append(f"High memory usage ({metric.memory_peak:.0f}MB)")
            elif metric.memory_peak > 100:
                priority_score += 1
                reasons.append(f"Medium memory usage ({metric.memory_peak:.0f}MB)")

            # I/O weight
            total_io = (metric.io_read_bytes + metric.io_write_bytes) / 1024 / 1024
            if total_io > 50:
                priority_score += 2
                reasons.append(f"High I/O ({total_io:.1f}MB)")
            elif total_io > 10:
                priority_score += 1
                reasons.append(f"Medium I/O ({total_io:.1f}MB)")

            if priority_score > 0:
                analysis["optimization_priorities"].append(
                    {"tool": metric.tool_name, "priority_score": priority_score, "reasons": reasons}
                )

        # Sort by priority
        analysis["optimization_priorities"].sort(key=lambda x: x["priority_score"], reverse=True)

        return analysis

    def generate_report(self, analysis: Dict) -> str:
        """Generate performance analysis report"""
        report = f"""# Performance Profiling Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tools Measured**: {len(self.results)}

## Executive Summary

### Slowest Tools

"""

        for item in analysis.get("slowest_tools", [])[:3]:
            report += f"- **{item['tool']}**: {item['time']:.3f}s -> {item['potential_speedup']}\n"

        report += "\n### Memory Intensive Tools\n\n"

        for item in analysis.get("memory_intensive", [])[:3]:
            report += (
                f"- **{item['tool']}**: Peak {item['peak_mb']:.1f}MB, Avg {item['avg_mb']:.1f}MB -> {item['optimization']}\n"
            )

        report += "\n### I/O Intensive Tools\n\n"

        for item in analysis.get("io_intensive", [])[:3]:
            report += (
                f"- **{item['tool']}**: Read {item['read_mb']:.1f}MB, "
                f"Write {item['write_mb']:.1f}MB -> {item['optimization']}\n"
            )

        report += "\n## Optimization Priorities\n\n"

        for i, item in enumerate(analysis.get("optimization_priorities", []), 1):
            report += f"### {i}. {item['tool']} (Priority: {item['priority_score']})\n\n"
            for reason in item["reasons"]:
                report += f"- {reason}\n"
            report += "\n"

        report += "## Detailed Measurement Results\n\n"
        report += "| Tool | Execution Time | Peak Memory | Avg Memory | CPU % | I/O Read | I/O Write |\n"
        report += "|------|----------------|-------------|------------|-------|----------|------------|\n"

        for metric in self.results:
            report += (
                f"| {metric.tool_name} | {metric.execution_time:.3f}s | "
                f"{metric.memory_peak:.1f}MB | {metric.memory_average:.1f}MB | "
                f"{metric.cpu_percent:.1f}% | {metric.io_read_bytes/1024/1024:.1f}MB | "
                f"{metric.io_write_bytes/1024/1024:.1f}MB |\n"
            )

        return report

    def save_results(self):
        """Save results"""
        # JSON
        json_path = self.output_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.results], f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] {json_path}")

        # Analysis
        analysis = self.analyze_bottlenecks()

        # Report
        report = self.generate_report(analysis)
        report_path = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"[SAVED] {report_path}")

        return analysis


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Performance Profiler")
    parser.add_argument("--tool", type=str, help="Specific tool to profile")
    parser.add_argument("--all", action="store_true", help="Benchmark all tools")

    args = parser.parse_args()

    profiler = PerformanceProfiler()

    if args.all:
        profiler.benchmark_all_tools()
        analysis = profiler.save_results()

        print("\n" + "=" * 60)
        print("OPTIMIZATION PRIORITIES")
        print("=" * 60)

        for item in analysis.get("optimization_priorities", []):
            print(f"\n{item['tool']} (Score: {item['priority_score']})")
            for reason in item["reasons"]:
                print(f"  - {reason}")

    elif args.tool:
        script_path = Path(args.tool)
        if not script_path.exists():
            script_path = Path.cwd() / "scripts" / args.tool

        if script_path.exists():
            profiler.profile_script(script_path)
            profiler.save_results()
        else:
            print(f"[ERROR] Tool not found: {args.tool}")

    else:
        print("Usage: python performance_profiler.py --all")


if __name__ == "__main__":
    main()
