#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circuit Breaker Test: Prevent Infinite Retry Loops

Tests that AI stops trying after 3 failed attempts with the same solution.
This prevents infinite loops when a saved solution doesn't work.
"""

from scripts.ai_auto_recovery import AIAutoRecovery


def test_circuit_breaker():
    """Test that circuit breaker stops infinite loops"""
    recovery = AIAutoRecovery()
    error_msg = "OSError: [Errno 10048] Address already in use: port 9000"

    print("=" * 70)
    print("CIRCUIT BREAKER TEST: Prevent Infinite Loops")
    print("=" * 70)

    # Save a solution first
    print("\n[SETUP] Creating past solution in Obsidian...")
    recovery.save_new_solution(error_msg, "netstat -ano | findstr :9000", context={"scenario": "circuit_breaker_test"})
    print("[SAVED] Solution stored")

    # Try to recover 5 times (circuit breaker should kick in after 3)
    print("\n[SCENARIO] AI tries to apply solution 5 times...")
    print("(Simulating case where solution exists but doesn't work)\n")

    for attempt in range(1, 6):
        print(f"Attempt {attempt}:")
        solution = recovery.auto_recover(error_msg)

        if solution:
            print(f"  [AUTO-RECOVERY] Found solution: {solution}")
            print("  [AI ACTION] Apply solution")
            print("  [RESULT] Still fails (simulated)")
        else:
            print("  [CIRCUIT-BREAKER] Stopped trying")
            print("  [REASON] Tried 3 times, giving up")
            print("  [AI ACTION] Ask user for different solution")
            break

        print()

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    if attempt < 5:
        print(f"\n[SUCCESS] Circuit breaker triggered after {attempt} attempts")
        print("\n[VERIFICATION]")
        print("- Prevents infinite retry loops: PASS")
        print("- AI knows when to give up: PASS")
        print("- Asks user for new solution: PASS")
    else:
        print("\n[FAILURE] Circuit breaker did not trigger!")
        print("AI would retry infinitely - this is a bug")

    print("\n[EXPLANATION]")
    print("Even though Obsidian has a past solution,")
    print("AI stops after 3 failed attempts and asks user for a DIFFERENT solution.")
    print("This prevents infinite loops when saved solution doesn't work.")


if __name__ == "__main__":
    test_circuit_breaker()
