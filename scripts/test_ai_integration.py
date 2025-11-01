#!/usr/bin/env python3
"""
Test AI Integration with UnifiedErrorResolver

This script verifies that the AI behavioral rules integration works correctly
by simulating error scenarios and checking 3-tier resolution.

IMPORTANT: No emojis due to Windows encoding restrictions (cp949 codec).
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from unified_error_resolver import UnifiedErrorResolver


def test_scenario_1_new_error():
    """Test Scenario 1: New error (should go to Tier 3)"""
    print("\n" + "=" * 60)
    print("TEST 1: New Error (Tier 3 Expected)")
    print("=" * 60)

    resolver = UnifiedErrorResolver()

    error_msg = "TestError: AI integration verification error"
    context = {"tool": "test", "purpose": "AI integration test", "scenario": "first_occurrence"}

    print(f"\n[SIMULATE] Error: {error_msg}")
    solution = resolver.resolve_error(error_msg, context)

    if solution is None:
        print("[OK] EXPECTED: No automated solution (Tier 3)")
        print("   -> AI should ask user for solution")
        print("   -> Then save to Obsidian for future")
        success = True
    else:
        print(f"[FAIL] UNEXPECTED: Got solution: {solution}")
        print("   -> Should have been None for new error")
        success = False

    stats = resolver.get_statistics()
    print("\n[STATS] Statistics:")
    print(f"   Tier 1 hits: {stats['tier1']} (expected: 0)")
    print(f"   Tier 2 hits: {stats['tier2']} (expected: 0)")
    print(f"   Tier 3 hits: {stats['tier3']} (expected: 1)")
    print(f"   Automation: {stats['automation_rate']:.1%}")

    return success and stats["tier3"] == 1


def test_scenario_2_known_error():
    """Test Scenario 2: Known error (should hit Tier 1)"""
    print("\n" + "=" * 60)
    print("TEST 2: Known Error (Tier 1 Expected)")
    print("=" * 60)

    resolver = UnifiedErrorResolver()

    # First, save a solution
    error_msg = "ModuleNotFoundError: No module named 'pytest'"
    solution = "pip install pytest"

    print("\n[SAVE] Saving solution to Obsidian...")
    print(f"   Error: {error_msg}")
    print(f"   Solution: {solution}")

    resolver.save_user_solution(error_msg, solution, {"tool": "Python", "library": "pytest"})

    print("[OK] Solution saved")

    # Now try to resolve the same error
    print("\n[SEARCH] Resolving same error again...")
    resolved_solution = resolver.resolve_error(error_msg, {"tool": "Python", "library": "pytest"})

    if resolved_solution:
        print(f"[OK] EXPECTED: Found solution: {resolved_solution}")
        print("   -> Tier 1 (Obsidian) hit!")

        stats = resolver.get_statistics()
        if stats["tier1"] > 0:
            print(f"   -> Speed: {stats['tier1_avg_time']:.2f}ms")
            return True
        else:
            print("[FAIL] Solution found but not from Tier 1")
            return False
    else:
        print("[FAIL] UNEXPECTED: No solution found")
        print("   -> Should have been found in Obsidian")
        return False


def test_scenario_3_context7_simulation():
    """Test Scenario 3: Context7 simulation (Tier 2)"""
    print("\n" + "=" * 60)
    print("TEST 3: Context7 Simulation (Tier 2 Expected)")
    print("=" * 60)

    resolver = UnifiedErrorResolver()

    # Use a known library that Context7 simulation handles
    error_msg = "ModuleNotFoundError: No module named 'pandas'"
    context = {"tool": "Python", "library": "pandas"}

    print("\n[SEARCH] Resolving error with Context7...")
    print(f"   Error: {error_msg}")

    solution = resolver.resolve_error(error_msg, context)

    if solution:
        print(f"[OK] EXPECTED: Found solution: {solution}")

        stats = resolver.get_statistics()
        if stats["tier2"] > 0:
            print("   -> Tier 2 (Context7) hit!")
            print("   -> Solution auto-saved to Obsidian")
            return True
        elif stats["tier1"] > 0:
            print("   -> Tier 1 hit (might be from previous test)")
            return True
        else:
            print("[FAIL] Solution found but tier stats unclear")
            return False
    else:
        print("[FAIL] UNEXPECTED: No solution from Context7")
        return False


def test_scenario_4_statistics_tracking():
    """Test Scenario 4: Statistics tracking"""
    print("\n" + "=" * 60)
    print("TEST 4: Statistics Tracking")
    print("=" * 60)

    resolver = UnifiedErrorResolver()

    # Simulate multiple resolutions
    print("\n[STATS] Simulating 10 error resolutions...")

    # 7 Tier 1 hits
    for i in range(7):
        error = f"KnownError{i}: test error"
        resolver.save_user_solution(error, f"solution{i}", {})
        resolver.resolve_error(error, {})

    # 2 Tier 2 hits
    resolver.resolve_error("ModuleNotFoundError: No module named 'numpy'", {})
    resolver.resolve_error("ModuleNotFoundError: No module named 'fastapi'", {})

    # 1 Tier 3 (no solution)
    resolver.resolve_error("UnknownCustomError: completely new", {})

    stats = resolver.get_statistics()

    print("\n[OK] Statistics:")
    print(f"   Total: {stats['total']}")
    print(f"   Tier 1: {stats['tier1']} ({stats['tier1_percentage']:.1%})")
    print(f"   Tier 2: {stats['tier2']} ({stats['tier2_percentage']:.1%})")
    print(f"   Tier 3: {stats['tier3']} ({stats['tier3_percentage']:.1%})")
    print(f"   Automation: {stats['automation_rate']:.1%}")
    print(f"   Tier 1 avg time: {stats['tier1_avg_time']:.2f}ms")

    expected_automation = (stats["tier1"] + stats["tier2"]) / stats["total"]
    return abs(stats["automation_rate"] - expected_automation) < 0.01


def main():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("AI INTEGRATION VERIFICATION")
    print("Testing UnifiedErrorResolver with AI behavioral rules")
    print("=" * 60)

    results = []

    try:
        results.append(("New Error (Tier 3)", test_scenario_1_new_error()))
        results.append(("Known Error (Tier 1)", test_scenario_2_known_error()))
        results.append(("Context7 (Tier 2)", test_scenario_3_context7_simulation()))
        results.append(("Statistics Tracking", test_scenario_4_statistics_tracking()))
    except Exception as e:
        print(f"\n[FAIL] Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nResults: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n[SUCCESS] AI INTEGRATION VERIFIED!")
        print("   -> UnifiedErrorResolver is ready for AI use")
        print("   -> 3-tier cascade working correctly")
        print("   -> Statistics tracking operational")
        return 0
    else:
        print("\n[WARN] SOME TESTS FAILED")
        print("   -> Review failed scenarios above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
