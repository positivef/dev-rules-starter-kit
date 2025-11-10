#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heavy Tools Benchmark - Performance measurement for heavy tools"""

import time
import subprocess
import sys


def measure_script(script_name, args=None, timeout=300):
    """Measure script execution time"""
    args = args or []
    print(f"\n[BENCHMARK] {script_name} {' '.join(args)}")
    print("-" * 60)

    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"] + args, capture_output=True, text=True, timeout=timeout
        )
        end = time.time()
        elapsed = end - start

        print(f"Time: {elapsed:.3f}s")
        print(f"Success: {result.returncode == 0}")

        if result.returncode != 0:
            print(f"Error (first 300 chars): {result.stderr[:300]}")
        else:
            # Show last few lines of output
            lines = result.stdout.strip().split("\n")
            if len(lines) > 5:
                print("Output (last 5 lines):")
                for line in lines[-5:]:
                    print(f"  {line}")
            else:
                print(f"Output: {result.stdout[:200]}")

        return elapsed, result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {timeout}s")
        return timeout, False


# Measure heavy tools
results = {}

print("=" * 60)
print("HEAVY TOOLS PERFORMANCE BENCHMARK")
print("=" * 60)

# 1. auto_improver.py --dry-run (expected: 3-5s)
print("\n[1/2] Auto-Improver (Constitution violation check)")
results["auto_improver"] = measure_script("auto_improver.py", ["--dry-run"], timeout=60)

# 2. auto_test_generator.py --dry-run (expected: 5-10s)
print("\n[2/2] Auto Test Generator (test generation)")
results["auto_test_generator"] = measure_script("auto_test_generator.py", ["--dry-run"], timeout=60)

# Summary
print("\n" + "=" * 60)
print("BENCHMARK SUMMARY")
print("=" * 60)

total_time = 0
for name, (time_sec, success) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
    status = "OK" if success else "FAIL"
    print(f"{name:30s}: {time_sec:6.3f}s [{status}]")
    if success:
        total_time += time_sec

print(f"\n{'Total (successful)':30s}: {total_time:6.3f}s")

# Detailed analysis
print("\n" + "=" * 60)
print("BOTTLENECK ANALYSIS")
print("=" * 60)

# Find slowest
slowest = max(results.items(), key=lambda x: x[1][0])
print(f"\nSlowest tool: {slowest[0]} ({slowest[1][0]:.3f}s)")

# Priority recommendations
print("\nOptimization priority:")

if slowest[1][0] > 5:
    print(f"  1. [HIGH] Worker Pool parallelization - {slowest[0]}")
    print(f"     Expected effect: {slowest[1][0]:.1f}s -> {slowest[1][0]*0.4:.1f}s (60% improvement)")
elif slowest[1][0] > 2:
    print(f"  1. [MEDIUM] Caching and deduplication - {slowest[0]}")
    print(f"     Expected effect: {slowest[1][0]:.1f}s -> {slowest[1][0]*0.6:.1f}s (40% improvement)")
else:
    print("  1. [LOW] Only micro-optimizations needed")
    print(f"     All tools under {max(t for _, (t, _) in results.items()):.1f}s")

# Parallelization analysis
print("\nParallelization potential:")
if total_time > 5:
    print(f"  - Sequential execution: {total_time:.1f}s")
    print(f"  - Parallel execution: {max(t for _, (t, _) in results.items()):.1f}s")
    print(f"  - Time saved: {total_time - max(t for _, (t, _) in results.items()):.1f}s")
else:
    print(f"  - Total time is {total_time:.1f}s - parallelization has minimal effect")

# Reality check
print("\n" + "=" * 60)
print("REALITY CHECK - Actual time savings calculation")
print("=" * 60)

# Assumption: 1 run per week
weekly_runs = 1
weeks_per_year = 52

before_time = total_time * weekly_runs * weeks_per_year / 3600  # hours
print("\nCurrent state (after automation):")
print(f"  - {weekly_runs} runs/week")
print(f"  - Yearly: {before_time:.1f} hours")

# Manual execution time (assumption)
manual_time_per_run = 30  # minutes
manual_yearly = manual_time_per_run * weekly_runs * weeks_per_year / 60  # hours

print("\nBefore automation (manual execution):")
print(f"  - Per run: {manual_time_per_run} minutes")
print(f"  - Yearly: {manual_yearly:.1f} hours")

savings = manual_yearly - before_time
print("\nActual savings:")
print(f"  - Yearly: {savings:.1f} hours")
print(f"  - Improvement rate: {savings/manual_yearly*100:.1f}%")

# Additional optimization effects
if slowest[1][0] > 2:
    optimized_time = total_time * 0.6  # 40% improvement
    optimized_yearly = optimized_time * weekly_runs * weeks_per_year / 3600
    additional_savings = before_time - optimized_yearly

    print("\nWith additional optimization:")
    print(f"  - Additional savings: {additional_savings:.1f} hours/year")
    print(f"  - Total savings: {savings + additional_savings:.1f} hours/year")
else:
    print("\nAdditional optimization:")
    print("  - Effect: minimal (<0.5 hours/year)")
