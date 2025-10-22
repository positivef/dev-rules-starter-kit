"""Example: VerificationCache Integration with Phase A RuffVerifier

This example demonstrates how the VerificationCache will be integrated
with the existing RuffVerifier in Phase A to provide intelligent caching
and avoid redundant file analysis.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.verification_cache import VerificationCache, VerificationResult, RuffViolation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CachedRuffVerifier:
    """RuffVerifier with intelligent caching

    Wraps the existing RuffVerifier with VerificationCache to avoid
    re-analyzing unchanged files.
    """

    def __init__(self, cache_dir: Path = Path("RUNS/.cache")):
        """Initialize cached verifier

        Args:
            cache_dir: Directory for cache storage
        """
        self.cache = VerificationCache(
            cache_dir=cache_dir,
            ttl_seconds=300,  # 5 minutes
            max_entries=1000,
        )

    def verify_file(self, file_path: Path) -> VerificationResult:
        """Verify file with caching

        Args:
            file_path: Path to file to verify

        Returns:
            VerificationResult from cache or fresh verification
        """
        # Try to get from cache
        cached_result = self.cache.get(file_path)

        if cached_result is not None:
            logger.info(f"[CACHE HIT] {file_path.name} - skipping analysis")
            return cached_result

        logger.info(f"[CACHE MISS] {file_path.name} - running verification")

        # Run actual verification (this would call real RuffVerifier)
        result = self._run_ruff_verification(file_path)

        # Store in cache
        self.cache.put(file_path, result, mode="fast")

        return result

    def _run_ruff_verification(self, file_path: Path) -> VerificationResult:
        """Mock Ruff verification (replace with actual RuffVerifier call)

        Args:
            file_path: Path to file to verify

        Returns:
            VerificationResult
        """
        # This is a mock - in real implementation, this would call:
        # return self.ruff_verifier.verify_file(file_path)

        # Mock: simulate finding violations
        violations = [RuffViolation(code="F401", message="'os' imported but unused", line=1, column=8, fix_available=True)]

        return VerificationResult(file_path=file_path, passed=False, violations=violations, duration_ms=150.0, error=None)


def demonstrate_caching():
    """Demonstrate cache effectiveness"""

    print("\n" + "=" * 60)
    print("VerificationCache Integration Example")
    print("=" * 60 + "\n")

    # Create cached verifier
    verifier = CachedRuffVerifier()

    # Test file
    test_file = Path("scripts/critical_file_detector.py")

    # First verification - cache miss
    print("First verification (cache miss expected):")
    result1 = verifier.verify_file(test_file)
    print(f"  Result: {result1.passed}, Violations: {len(result1.violations)}")
    print(f"  Duration: {result1.duration_ms}ms\n")

    # Second verification - cache hit
    print("Second verification (cache hit expected):")
    result2 = verifier.verify_file(test_file)
    print(f"  Result: {result2.passed}, Violations: {len(result2.violations)}")
    print(f"  Duration: {result2.duration_ms}ms (from cache!)\n")

    # Show cache statistics
    print("Cache statistics:")
    stats = verifier.cache.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Integration Benefits:")
    print("=" * 60)
    print("1. Avoid re-analyzing unchanged files")
    print("2. Faster development workflow (5-10x speedup)")
    print("3. Reduced CPU usage in file watcher")
    print("4. Persistent cache across sessions")
    print("5. Automatic expiration (TTL) and eviction (LRU)")
    print("=" * 60 + "\n")


def demonstrate_batch_processing():
    """Demonstrate batch file processing with caching"""

    print("\n" + "=" * 60)
    print("Batch Processing with Cache")
    print("=" * 60 + "\n")

    verifier = CachedRuffVerifier()

    # Simulate processing multiple files
    files = [
        Path("scripts/critical_file_detector.py"),
        Path("scripts/verification_cache.py"),
        Path("scripts/dev_assistant.py"),
    ]

    # First pass
    print("First pass (cache misses):")
    for file_path in files:
        if file_path.exists():
            result = verifier.verify_file(file_path)
            print(f"  {file_path.name}: {result.passed}")

    # Second pass
    print("\nSecond pass (cache hits):")
    for file_path in files:
        if file_path.exists():
            result = verifier.verify_file(file_path)
            print(f"  {file_path.name}: {result.passed}")

    # Statistics
    print("\nCache statistics:")
    stats = verifier.cache.stats()
    print(f"  Total cached files: {stats['size']}")
    print(f"  Total cache hits: {stats['total_hits']}")
    print(f"  Hit rate: {stats['total_hits'] / (stats['size'] * 2) * 100:.1f}%")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_caching()
    demonstrate_batch_processing()
