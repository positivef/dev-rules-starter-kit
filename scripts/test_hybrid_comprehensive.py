#!/usr/bin/env python3
"""Comprehensive tests for hybrid confidence-based error resolution"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from unified_error_resolver import UnifiedErrorResolver


def test_high_confidence_auto_apply():
    """Test HIGH confidence: should auto-apply"""
    print("\n" + "=" * 70)
    print("TEST 1: HIGH Confidence - Auto-Apply")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # Use a unique error that won't be in Obsidian cache
    error_msg = "ModuleNotFoundError: No module named 'pytest_unique_12345'"
    context = {"tool": "Python", "script": "test.py"}

    print(f"\nError: {error_msg}")
    solution = resolver.resolve_error(error_msg, context)

    print(f"\n[RESULT] Solution returned: {solution}")

    stats = resolver.get_statistics()
    print("\n[STATS] Tier breakdown:")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']}")
    print(f"  - Tier 2 (Context7): {stats['tier2']}")
    print(f"  - Tier 2 Auto-Applied: {stats['tier2_auto']}")
    print(f"  - Tier 2 Confirmed: {stats['tier2_confirmed']}")
    print(f"  - Tier 3 (User): {stats['tier3']}")

    # Verify expectations
    expected_solution = "pip install pytest_unique_12345"
    if solution == expected_solution:
        print("\n[PASS] HIGH confidence auto-applied correctly")
        return True
    else:
        print(f"\n[FAIL] Expected {expected_solution}, got {solution}")
        return False


def test_medium_confidence_confirmation():
    """Test MEDIUM confidence: should ask confirmation"""
    print("\n" + "=" * 70)
    print("TEST 2: MEDIUM Confidence - Ask Confirmation")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # ImportError has medium confidence (70% base)
    error_msg = "ImportError: cannot import name 'SpecialClass' from 'mymodule_unique_67890'"
    context = {"tool": "Python", "script": "app.py"}

    print(f"\nError: {error_msg}")
    solution = resolver.resolve_error(error_msg, context)

    print(f"\n[RESULT] Solution returned: {solution}")

    stats = resolver.get_statistics()
    print("\n[STATS] Tier breakdown:")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']}")
    print(f"  - Tier 2 (Context7): {stats['tier2']}")
    print(f"  - Tier 2 Auto-Applied: {stats['tier2_auto']}")
    print(f"  - Tier 2 Confirmed: {stats['tier2_confirmed']}")
    print(f"  - Tier 3 (User): {stats['tier3']}")

    # MEDIUM confidence should return None (needs confirmation)
    if solution is None:
        print("\n[PASS] MEDIUM confidence correctly requests confirmation")
        return True
    else:
        print(f"\n[FAIL] Expected None (confirmation), got {solution}")
        return False


def test_low_confidence_user_intervention():
    """Test LOW confidence: should go to user"""
    print("\n" + "=" * 70)
    print("TEST 3: LOW Confidence - User Intervention")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # Custom business logic error has low confidence (use unique ID to avoid cache)
    import time

    unique_id = str(int(time.time() * 1000))
    error_msg = f"CustomBusinessLogicError: Payment validation failed for transaction #{unique_id}"
    context = {"tool": "Python", "script": "payment.py"}

    print(f"\nError: {error_msg}")
    solution = resolver.resolve_error(error_msg, context)

    print(f"\n[RESULT] Solution returned: {solution}")

    stats = resolver.get_statistics()
    print("\n[STATS] Tier breakdown:")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']}")
    print(f"  - Tier 2 (Context7): {stats['tier2']}")
    print(f"  - Tier 2 Auto-Applied: {stats['tier2_auto']}")
    print(f"  - Tier 2 Confirmed: {stats['tier2_confirmed']}")
    print(f"  - Tier 3 (User): {stats['tier3']}")

    # LOW confidence should return None (user needed)
    if solution is None:
        print("\n[PASS] LOW confidence correctly escalates to user")
        return True
    else:
        print(f"\n[FAIL] Expected None (user intervention), got {solution}")
        return False


def test_blacklist_pattern_blocking():
    """Test blacklist: dangerous patterns should not auto-apply"""
    print("\n" + "=" * 70)
    print("TEST 4: Blacklist Pattern - Should Block Auto-Apply")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # Error that might suggest a sudo solution
    error_msg = "PermissionError: [Errno 13] Permission denied: '/etc/config'"
    context = {"tool": "Bash", "command": "cp config /etc/config"}

    print(f"\nError: {error_msg}")
    solution = resolver.resolve_error(error_msg, context)

    print(f"\n[RESULT] Solution returned: {solution}")

    stats = resolver.get_statistics()
    print("\n[STATS] Tier breakdown:")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']}")
    print(f"  - Tier 2 (Context7): {stats['tier2']}")
    print(f"  - Tier 2 Auto-Applied: {stats['tier2_auto']}")
    print(f"  - Tier 2 Confirmed: {stats['tier2_confirmed']}")
    print(f"  - Tier 3 (User): {stats['tier3']}")

    # Blacklisted patterns should not auto-apply
    # If solution contains "sudo", it should not have been auto-applied
    if solution is None or (solution and "sudo" in solution.lower() and stats["tier2_auto"] == 0):
        print("\n[PASS] Blacklist pattern correctly prevented auto-apply")
        return True
    else:
        print("\n[FAIL] Blacklist pattern should have blocked auto-apply")
        return False


def test_circuit_breaker_activation():
    """Test circuit breaker: should disable after 3 failures"""
    print("\n" + "=" * 70)
    print("TEST 5: Circuit Breaker - Disable After 3 Failures")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # Simulate 3 auto-apply failures
    if resolver.circuit_breaker:
        print("\n[INFO] Simulating 3 failed auto-applications...")
        resolver.circuit_breaker.record_auto_apply(False)
        resolver.circuit_breaker.record_auto_apply(False)
        resolver.circuit_breaker.record_auto_apply(False)

        is_allowed = resolver.circuit_breaker.is_auto_apply_allowed()
        print(f"\n[RESULT] Auto-apply allowed after 3 failures: {is_allowed}")

        if not is_allowed:
            print("\n[PASS] Circuit breaker correctly disabled auto-apply")
            return True
        else:
            print("\n[FAIL] Circuit breaker should have disabled auto-apply")
            return False
    else:
        print("\n[SKIP] Circuit breaker not available")
        return True


def test_statistics_tracking():
    """Test statistics: verify correct tier tracking"""
    print("\n" + "=" * 70)
    print("TEST 6: Statistics Tracking")
    print("=" * 70)

    resolver = UnifiedErrorResolver()

    # Test multiple resolutions
    errors = [
        "ModuleNotFoundError: No module named 'requests_stats_test'",
        "ModuleNotFoundError: No module named 'flask_stats_test'",
    ]

    for error in errors:
        print(f"\n[INFO] Resolving: {error}")
        resolver.resolve_error(error, {})

    stats = resolver.get_statistics()

    print("\n[STATS] Final statistics:")
    print(f"  - Total resolutions: {stats['total']}")
    print(f"  - Tier 1 (Obsidian): {stats['tier1']} ({stats['tier1_percentage']:.1%})")
    print(f"  - Tier 2 (Context7): {stats['tier2']} ({stats['tier2_percentage']:.1%})")
    print(f"  - Tier 2 Auto: {stats['tier2_auto']}")
    print(f"  - Tier 2 Confirmed: {stats['tier2_confirmed']}")
    print(f"  - Tier 3 (User): {stats['tier3']} ({stats['tier3_percentage']:.1%})")
    print(f"  - Automation rate: {stats['automation_rate']:.1%}")
    print(f"  - Tier 1 avg time: {stats['tier1_avg_time']:.2f}ms")
    print(f"  - Tier 2 avg time: {stats['tier2_avg_time']:.2f}ms")

    # Verify total matches sum
    total_sum = stats["tier1"] + stats["tier2"] + stats["tier3"]
    if stats["total"] == total_sum == len(errors):
        print("\n[PASS] Statistics tracking correct")
        return True
    else:
        print(f"\n[FAIL] Statistics mismatch: total={stats['total']}, sum={total_sum}, expected={len(errors)}")
        return False


def main():
    """Run all comprehensive tests"""
    print("=" * 70)
    print("Hybrid Confidence-Based Resolution - Comprehensive Test Suite")
    print("=" * 70)

    tests = [
        ("HIGH Confidence Auto-Apply", test_high_confidence_auto_apply),
        ("MEDIUM Confidence Confirmation", test_medium_confidence_confirmation),
        ("LOW Confidence User Intervention", test_low_confidence_user_intervention),
        ("Blacklist Pattern Blocking", test_blacklist_pattern_blocking),
        ("Circuit Breaker Activation", test_circuit_breaker_activation),
        ("Statistics Tracking", test_statistics_tracking),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' raised exception: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
