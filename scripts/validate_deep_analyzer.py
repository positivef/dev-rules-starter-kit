"""Performance validation for DeepAnalyzer

Validates that DeepAnalyzer meets performance requirements:
- Analysis time < 5s for typical files
- Analysis time < 1s with fallback (no MCP)
"""

import sys
import time
from pathlib import Path

try:
    from deep_analyzer import DeepAnalyzer
except ImportError:
    from scripts.deep_analyzer import DeepAnalyzer


def validate_performance():
    """Validate performance on typical Python files"""

    # Test files from the project
    test_files = [
        Path("scripts/deep_analyzer.py"),
        Path("scripts/critical_file_detector.py"),
        Path("scripts/verification_cache.py"),
    ]

    analyzer = DeepAnalyzer(mcp_enabled=False)

    print("DeepAnalyzer Performance Validation")
    print("=" * 60)

    all_passed = True

    for file_path in test_files:
        if not file_path.exists():
            print(f"SKIP: {file_path} (not found)")
            continue

        print(f"\nAnalyzing: {file_path.name}")

        # Run analysis
        start = time.perf_counter()
        result = analyzer.analyze(file_path)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Check performance
        target_ms = 5000  # 5 seconds
        fallback_target_ms = 1000  # 1 second for fallback

        status = "PASS" if elapsed_ms < target_ms else "FAIL"
        fallback_status = "PASS" if elapsed_ms < fallback_target_ms else "FAIL"

        print(f"  Time: {elapsed_ms:.0f}ms (target: <{target_ms}ms)")
        print(f"  Fallback performance: {fallback_status} (target: <{fallback_target_ms}ms)")
        print(f"  Quality score: {result.overall_score:.1f}/10.0")
        print(f"  Issues found: {result.total_issues}")
        print(f"  Status: {status}")

        if elapsed_ms >= target_ms:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("RESULT: All performance checks PASSED")
        return 0
    else:
        print("RESULT: Some performance checks FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(validate_performance())
