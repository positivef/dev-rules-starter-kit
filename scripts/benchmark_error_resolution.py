#!/usr/bin/env python3
"""
Benchmark script to compare OLD vs NEW error resolution systems

Usage:
    # Baseline (OLD system)
    python scripts/benchmark_error_resolution.py --mode simple --iterations 50

    # Hybrid (NEW system)
    python scripts/benchmark_error_resolution.py --mode hybrid --iterations 50

    # Compare results
    python scripts/compare_performance.py
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from unified_error_resolver import UnifiedErrorResolver


class ErrorResolutionBenchmark:
    """Benchmark error resolution system performance"""

    def __init__(self, mode: str = "hybrid", iterations: int = 50):
        self.mode = mode
        self.iterations = iterations
        self.results = []

        # Initialize resolver
        if mode == "simple":
            # Simulate OLD system by disabling confidence calc
            self.resolver = UnifiedErrorResolver()
            self.resolver.confidence_calc = None  # Disable hybrid
        else:
            self.resolver = UnifiedErrorResolver()

    def run_benchmark(self):
        """Run benchmark with predefined error scenarios"""
        print("=" * 70)
        print(f"Error Resolution Benchmark - Mode: {self.mode.upper()}")
        print("=" * 70)

        scenarios = self._get_test_scenarios()

        print(f"\nRunning {self.iterations} iterations...")
        print(f"Test scenarios: {len(scenarios)}")

        for i in range(self.iterations):
            scenario = scenarios[i % len(scenarios)]
            result = self._test_scenario(scenario)
            self.results.append(result)

            if (i + 1) % 10 == 0:
                print(f"Progress: {i+1}/{self.iterations} completed")

        stats = self._calculate_statistics()
        self._print_results(stats)
        self._save_results(stats)

    def _get_test_scenarios(self) -> List[Dict]:
        """Get predefined test scenarios"""
        return [
            # HIGH confidence scenarios (should auto-apply in hybrid)
            {
                "error": "ModuleNotFoundError: No module named 'pandas'",
                "context": {"tool": "Python", "library": "pandas"},
                "expected_tier": 2,
                "expected_auto": True,
            },
            {
                "error": "ModuleNotFoundError: No module named 'numpy'",
                "context": {"tool": "Python", "library": "numpy"},
                "expected_tier": 2,
                "expected_auto": True,
            },
            {
                "error": "ModuleNotFoundError: No module named 'requests'",
                "context": {"tool": "Python", "library": "requests"},
                "expected_tier": 2,
                "expected_auto": True,
            },
            {
                "error": "ModuleNotFoundError: No module named 'scipy'",
                "context": {"tool": "Python", "library": "scipy"},
                "expected_tier": 2,
                "expected_auto": True,
            },
            {
                "error": "ModuleNotFoundError: No module named 'matplotlib'",
                "context": {"tool": "Python", "library": "matplotlib"},
                "expected_tier": 2,
                "expected_auto": True,
            },
            # MEDIUM confidence scenarios (should ask user in hybrid)
            {
                "error": "ImportError: cannot import name 'SpecialClass' from 'mymodule'",
                "context": {"tool": "Python"},
                "expected_tier": 3,
                "expected_auto": False,
            },
            {
                "error": "ImportError: cannot import name 'Config' from 'settings'",
                "context": {"tool": "Python"},
                "expected_tier": 3,
                "expected_auto": False,
            },
            # LOW confidence scenarios (should skip to user)
            {
                "error": "CustomBusinessError: Payment validation failed",
                "context": {"tool": "Python"},
                "expected_tier": 3,
                "expected_auto": False,
            },
            {
                "error": "ValidationError: User input exceeds limit",
                "context": {"tool": "Python"},
                "expected_tier": 3,
                "expected_auto": False,
            },
            {
                "error": "AuthenticationError: Invalid token",
                "context": {"tool": "Python"},
                "expected_tier": 3,
                "expected_auto": False,
            },
        ]

    def _test_scenario(self, scenario: Dict) -> Dict:
        """Test a single error resolution scenario"""
        start_time = time.time()

        solution = self.resolver.resolve_error(scenario["error"], scenario["context"])

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000

        # Determine which tier resolved
        stats = self.resolver.get_statistics()
        tier = 1 if stats["tier1"] > 0 else (2 if solution else 3)
        auto_applied = solution is not None

        return {
            "error": scenario["error"],
            "tier": tier,
            "auto_applied": auto_applied,
            "elapsed_ms": elapsed_ms,
            "expected_tier": scenario.get("expected_tier"),
            "expected_auto": scenario.get("expected_auto"),
        }

    def _calculate_statistics(self) -> Dict:
        """Calculate aggregate statistics"""
        total = len(self.results)

        tier1_count = sum(1 for r in self.results if r["tier"] == 1)
        tier2_count = sum(1 for r in self.results if r["tier"] == 2 and r["auto_applied"])
        tier2_confirmed = sum(1 for r in self.results if r["tier"] == 2 and not r["auto_applied"])
        tier3_count = sum(1 for r in self.results if r["tier"] == 3)

        auto_count = tier1_count + tier2_count
        automation_rate = auto_count / total if total > 0 else 0

        user_intervention = tier2_confirmed + tier3_count
        user_intervention_rate = user_intervention / total if total > 0 else 0

        avg_time_ms = sum(r["elapsed_ms"] for r in self.results) / total if total > 0 else 0

        # Calculate accuracy (for hybrid mode)
        accuracy = None
        if self.mode == "hybrid":
            auto_results = [r for r in self.results if r["auto_applied"]]
            if auto_results:
                correct = sum(1 for r in auto_results if r.get("expected_auto") is True and r["auto_applied"] is True)
                accuracy = correct / len(auto_results)

        return {
            "mode": self.mode,
            "timestamp": datetime.now().isoformat(),
            "iterations": self.iterations,
            "total_errors": total,
            "tier1_hits": tier1_count,
            "tier2_auto": tier2_count,
            "tier2_confirmed": tier2_confirmed,
            "tier3_hits": tier3_count,
            "automation_rate": automation_rate,
            "user_intervention_rate": user_intervention_rate,
            "avg_resolution_time_ms": avg_time_ms,
            "accuracy": accuracy,
            "raw_results": self.results,
        }

    def _print_results(self, stats: Dict):
        """Print benchmark results"""
        print("\n" + "=" * 70)
        print(f"BENCHMARK RESULTS - {stats['mode'].upper()} MODE")
        print("=" * 70)

        print("\n[SUMMARY]")
        print(f"  Total Errors: {stats['total_errors']}")
        print(f"  Iterations: {stats['iterations']}")
        print(f"  Mode: {stats['mode']}")

        print("\n[TIER BREAKDOWN]")
        print(f"  Tier 1 (Obsidian): {stats['tier1_hits']} ({stats['tier1_hits']/stats['total_errors']*100:.1f}%)")
        print(f"  Tier 2 Auto: {stats['tier2_auto']} ({stats['tier2_auto']/stats['total_errors']*100:.1f}%)")
        print(f"  Tier 2 Confirmed: {stats['tier2_confirmed']} ({stats['tier2_confirmed']/stats['total_errors']*100:.1f}%)")
        print(f"  Tier 3 (User): {stats['tier3_hits']} ({stats['tier3_hits']/stats['total_errors']*100:.1f}%)")

        print("\n[KEY METRICS]")
        print(f"  Automation Rate: {stats['automation_rate']:.1%}")
        print(f"  User Intervention Rate: {stats['user_intervention_rate']:.1%}")
        print(f"  Avg Resolution Time: {stats['avg_resolution_time_ms']:.1f}ms")

        if stats["accuracy"] is not None:
            print(f"  Accuracy: {stats['accuracy']:.1%}")

        print("\n[TIME ANALYSIS]")
        times = [r["elapsed_ms"] for r in self.results]
        print(f"  Min: {min(times):.1f}ms")
        print(f"  Max: {max(times):.1f}ms")
        print(f"  Median: {sorted(times)[len(times)//2]:.1f}ms")

    def _save_results(self, stats: Dict):
        """Save benchmark results to file"""
        output_dir = Path("RUNS/benchmark")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stats['mode']}_{timestamp}.json"
        output_path = output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        print(f"\n[SAVED] Results saved to: {output_path}")

        # Also save as latest for easy comparison
        latest_path = output_dir / f"{stats['mode']}_latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        print(f"[SAVED] Latest results: {latest_path}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark error resolution system")
    parser.add_argument(
        "--mode",
        choices=["simple", "hybrid"],
        default="hybrid",
        help="Test mode: simple (OLD) or hybrid (NEW)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of test iterations (default: 50)",
    )

    args = parser.parse_args()

    benchmark = ErrorResolutionBenchmark(mode=args.mode, iterations=args.iterations)
    benchmark.run_benchmark()

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)

    if args.mode == "simple":
        print("\nNext step: Run hybrid mode benchmark")
        print("  python scripts/benchmark_error_resolution.py --mode hybrid")
    else:
        print("\nNext step: Compare results")
        print("  python scripts/compare_performance.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
