#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick Benchmark - Fast performance measurement"""

import time
import subprocess
import sys


def measure_script(script_name, args=None):
    """Measure script execution time"""
    args = args or []
    print(f"\n[BENCHMARK] {script_name}")
    print("-" * 50)

    start = time.time()
    result = subprocess.run([sys.executable, f"scripts/{script_name}"] + args, capture_output=True, text=True)
    end = time.time()

    elapsed = end - start
    print(f"Time: {elapsed:.3f}s")
    print(f"Success: {result.returncode == 0}")

    if result.returncode != 0:
        print(f"Error: {result.stderr[:200]}")

    return elapsed, result.returncode == 0


# Measure tools
results = {}

# 1. claude_md_updater.py (expected to be fast)
results["claude_md_updater"] = measure_script("claude_md_updater.py")

# 2. auto_doc_updater.py --dry-run (medium)
results["auto_doc_updater"] = measure_script("auto_doc_updater.py", ["--dry-run"])

# 3. constitutional_validator.py (expected to be fast)
results["constitutional_validator"] = measure_script("constitutional_validator.py")

# Summary
print("\n" + "=" * 50)
print("BENCHMARK SUMMARY")
print("=" * 50)

for name, (time_sec, success) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
    status = "OK" if success else "FAIL"
    print(f"{name:30s}: {time_sec:6.3f}s [{status}]")

# Priority analysis
print("\n" + "=" * 50)
print("OPTIMIZATION PRIORITY")
print("=" * 50)

slow_tools = [(n, t) for n, (t, s) in results.items() if t > 1.0 and s]
if slow_tools:
    print("\nSlow tools (>1s):")
    for name, time_sec in sorted(slow_tools, key=lambda x: x[1], reverse=True):
        potential_speedup = time_sec * 0.5  # 50% improvement assumption
        print(f"  - {name}: {time_sec:.3f}s -> {potential_speedup:.3f}s (Worker Pool)")
else:
    print("\nAll tools execute under 1s - only micro-optimizations needed")

print("\nRecommendations:")
if any(t > 2 for _, (t, _) in results.items()):
    print("  1. Implement Worker Pool parallel processing (expected 50% speedup)")
    print("  2. Improve caching strategy")
else:
    print("  1. Improve caching strategy first")
    print("  2. Remove duplicate validations")
