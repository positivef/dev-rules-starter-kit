#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heavy Tools Benchmark - 무거운 도구 성능 측정"""

import time
import subprocess
import sys


def measure_script(script_name, args=None, timeout=300):
    """스크립트 실행 시간 측정"""
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

# 1. auto_improver.py --dry-run (예상: 3-5초)
print("\n[1/2] Auto-Improver (Constitution 위반 검사)")
results["auto_improver"] = measure_script("auto_improver.py", ["--dry-run"], timeout=60)

# 2. auto_test_generator.py --dry-run (예상: 5-10초)
print("\n[2/2] Auto Test Generator (테스트 생성)")
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
print(f"\n가장 느린 도구: {slowest[0]} ({slowest[1][0]:.3f}s)")

# Priority recommendations
print("\n최적화 우선순위:")

if slowest[1][0] > 5:
    print(f"  1. [HIGH] Worker Pool 병렬화 - {slowest[0]}")
    print(f"     예상 효과: {slowest[1][0]:.1f}s -> {slowest[1][0]*0.4:.1f}s (60% 개선)")
elif slowest[1][0] > 2:
    print(f"  1. [MEDIUM] 캐싱 및 중복 제거 - {slowest[0]}")
    print(f"     예상 효과: {slowest[1][0]:.1f}s -> {slowest[1][0]*0.6:.1f}s (40% 개선)")
else:
    print("  1. [LOW] 마이크로 최적화만 필요")
    print(f"     모든 도구가 {max(t for _, (t, _) in results.items()):.1f}초 미만")

# Parallelization analysis
print("\n병렬화 가능성:")
if total_time > 5:
    print(f"  - 순차 실행 시: {total_time:.1f}s")
    print(f"  - 병렬 실행 시: {max(t for _, (t, _) in results.items()):.1f}s")
    print(f"  - 절감 시간: {total_time - max(t for _, (t, _) in results.items()):.1f}s")
else:
    print(f"  - 총 시간이 {total_time:.1f}s로 짧아 병렬화 효과 미미")

# Reality check
print("\n" + "=" * 60)
print("REALITY CHECK - 실제 절감 시간 계산")
print("=" * 60)

# 가정: 주 1회 전체 실행
weekly_runs = 1
weeks_per_year = 52

before_time = total_time * weekly_runs * weeks_per_year / 3600  # hours
print("\n현재 상태 (자동화 후):")
print(f"  - 주 {weekly_runs}회 실행")
print(f"  - 연간: {before_time:.1f}시간")

# 수동 실행 시간 (가정)
manual_time_per_run = 30  # minutes
manual_yearly = manual_time_per_run * weekly_runs * weeks_per_year / 60  # hours

print("\n자동화 전 (수동 실행):")
print(f"  - 실행당: {manual_time_per_run}분")
print(f"  - 연간: {manual_yearly:.1f}시간")

savings = manual_yearly - before_time
print("\n실제 절감:")
print(f"  - 연간: {savings:.1f}시간")
print(f"  - 개선율: {savings/manual_yearly*100:.1f}%")

# 추가 최적화 효과
if slowest[1][0] > 2:
    optimized_time = total_time * 0.6  # 40% improvement
    optimized_yearly = optimized_time * weekly_runs * weeks_per_year / 3600
    additional_savings = before_time - optimized_yearly

    print("\n추가 최적화 시:")
    print(f"  - 추가 절감: {additional_savings:.1f}시간/년")
    print(f"  - 총 절감: {savings + additional_savings:.1f}시간/년")
else:
    print("\n추가 최적화:")
    print("  - 효과: 미미 (<0.5시간/년)")
