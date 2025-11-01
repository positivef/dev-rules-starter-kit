#!/usr/bin/env python3
"""Quick integration test for hybrid resolution"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from unified_error_resolver import UnifiedErrorResolver


def main():
    print("=" * 60)
    print("Hybrid Resolution Quick Test")
    print("=" * 60)

    resolver = UnifiedErrorResolver()
    print("\n[OK] UnifiedErrorResolver initialized successfully")
    print(f"[OK] Confidence calculator: {resolver.confidence_calc is not None}")
    print(f"[OK] Circuit breaker: {resolver.circuit_breaker is not None}")

    # Test 1: High confidence case (should auto-apply)
    print("\n" + "=" * 60)
    print("TEST 1: High Confidence (pip install pandas)")
    print("=" * 60)
    solution = resolver.resolve_error("ModuleNotFoundError: No module named pandas", {})
    print(f"\n[RESULT] Returned solution: {solution}")

    stats = resolver.get_statistics()
    print(f'[STATS] Tier 2 auto: {stats["tier2_auto"]}')

    # Test 2: Blacklisted pattern (should not auto-apply)
    print("\n" + "=" * 60)
    print("TEST 2: Blacklisted Pattern (sudo command)")
    print("=" * 60)

    resolver2 = UnifiedErrorResolver()
    solution2 = resolver2.resolve_error("Service failed", {})
    print(f"\n[RESULT] Returned solution: {solution2}")

    print("\n" + "=" * 60)
    print("Quick Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
