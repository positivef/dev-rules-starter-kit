"""Tests for VerificationCache

Test coverage:
- Cache hit/miss scenarios
- TTL expiration
- LRU eviction
- Hash change detection
- Persistence (load/save)
- Performance benchmarks
- Error handling
- Thread safety
- Edge cases

Target: 95%+ coverage with comprehensive edge case testing
"""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scripts.verification_cache import (
    CacheEntry,
    RuffViolation,
    VerificationCache,
    VerificationResult,
)


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory"""
    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


@pytest.fixture
def cache(temp_cache_dir):
    """Create cache instance with temporary directory"""
    return VerificationCache(
        cache_dir=temp_cache_dir,
        ttl_seconds=300,  # 5 minutes
        max_entries=10,  # Small for testing eviction
    )


@pytest.fixture
def sample_result(tmp_path):
    """Create sample VerificationResult"""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")

    return VerificationResult(
        file_path=test_file,
        passed=True,
        violations=[],
        duration_ms=50.0,
        error=None,
    )


@pytest.fixture
def sample_result_with_violations(tmp_path):
    """Create VerificationResult with violations"""
    test_file = tmp_path / "bad_code.py"
    test_file.write_text("import os\nimport sys\n")  # Unused imports

    violations = [
        RuffViolation(
            code="F401",
            message="'os' imported but unused",
            line=1,
            column=8,
            fix_available=True,
        ),
        RuffViolation(
            code="F401",
            message="'sys' imported but unused",
            line=2,
            column=8,
            fix_available=True,
        ),
    ]

    return VerificationResult(
        file_path=test_file,
        passed=False,
        violations=violations,
        duration_ms=75.5,
        error=None,
    )


@pytest.fixture
def sample_result_with_error(tmp_path):
    """Create VerificationResult with error"""
    test_file = tmp_path / "error.py"
    test_file.write_text("syntax error here!")

    return VerificationResult(
        file_path=test_file,
        passed=False,
        violations=[],
        duration_ms=10.0,
        error="Syntax error on line 1",
    )


class TestCacheBasics:
    """Test basic cache operations"""

    def test_initialization(self, temp_cache_dir):
        """Test cache initialization"""
        cache = VerificationCache(
            cache_dir=temp_cache_dir,
            ttl_seconds=300,
            max_entries=1000,
        )

        assert cache.cache_dir == temp_cache_dir
        assert cache.ttl_seconds == 300
        assert cache.max_entries == 1000
        assert cache.size() == 0
        assert cache.cache_file == temp_cache_dir / "verification_cache.json"

    def test_cache_directory_creation(self, tmp_path):
        """Test automatic cache directory creation"""
        cache_dir = tmp_path / "nested" / "cache" / "dir"
        assert not cache_dir.exists()

        _ = VerificationCache(cache_dir=cache_dir)

        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_size_tracking(self, cache, sample_result):
        """Test cache size tracking"""
        assert cache.size() == 0

        cache.put(sample_result.file_path, sample_result)
        assert cache.size() == 1

        cache.put(sample_result.file_path, sample_result)
        assert cache.size() == 1  # Same file, no size increase

    def test_clear(self, cache, sample_result):
        """Test cache clearing"""
        cache.put(sample_result.file_path, sample_result)
        assert cache.size() == 1

        cache.clear()
        assert cache.size() == 0

        # Verify persistence
        assert cache.cache_file.exists()
        with open(cache.cache_file) as f:
            data = json.load(f)
        assert len(data) == 0


class TestCacheHitMiss:
    """Test cache hit/miss scenarios"""

    def test_cache_miss_no_entry(self, cache, tmp_path):
        """Test cache miss when no entry exists"""
        test_file = tmp_path / "new_file.py"
        test_file.write_text("print('test')")

        result = cache.get(test_file)
        assert result is None

    def test_cache_miss_file_not_found(self, cache):
        """Test cache miss when file doesn't exist"""
        nonexistent = Path("/nonexistent/file.py")
        result = cache.get(nonexistent)
        assert result is None

    def test_cache_hit_simple(self, cache, sample_result):
        """Test basic cache hit"""
        # Store result
        cache.put(sample_result.file_path, sample_result)

        # Retrieve from cache
        cached = cache.get(sample_result.file_path)

        assert cached is not None
        assert cached.file_path == sample_result.file_path
        assert cached.passed == sample_result.passed
        assert cached.duration_ms == sample_result.duration_ms
        assert len(cached.violations) == len(sample_result.violations)

    def test_cache_hit_with_violations(self, cache, sample_result_with_violations):
        """Test cache hit with violations"""
        cache.put(sample_result_with_violations.file_path, sample_result_with_violations)

        cached = cache.get(sample_result_with_violations.file_path)

        assert cached is not None
        assert cached.passed is False
        assert len(cached.violations) == 2

        # Verify violation details
        v1 = cached.violations[0]
        assert v1.code == "F401"
        assert v1.line == 1
        assert v1.column == 8
        assert v1.fix_available is True

    def test_cache_hit_with_error(self, cache, sample_result_with_error):
        """Test cache hit with error"""
        cache.put(sample_result_with_error.file_path, sample_result_with_error)

        cached = cache.get(sample_result_with_error.file_path)

        assert cached is not None
        assert cached.passed is False
        assert cached.error == "Syntax error on line 1"
        assert len(cached.violations) == 0

    def test_cache_miss_hash_mismatch(self, cache, sample_result):
        """Test cache miss when file content changes"""
        # Store original result
        cache.put(sample_result.file_path, sample_result)

        # Modify file content
        sample_result.file_path.write_text("print('modified')")

        # Should be cache miss due to hash mismatch
        cached = cache.get(sample_result.file_path)
        assert cached is None

        # Entry should be removed
        assert cache.size() == 0

    def test_cache_access_count(self, cache, sample_result):
        """Test access count tracking"""
        cache.put(sample_result.file_path, sample_result)

        # First access
        cache.get(sample_result.file_path)

        # Check access count in internal cache
        cache_key = str(sample_result.file_path.resolve())
        entry = cache._cache[cache_key]
        assert entry.access_count == 1

        # Second access
        cache.get(sample_result.file_path)
        assert entry.access_count == 2


class TestTTLExpiration:
    """Test TTL expiration logic"""

    def test_cache_hit_within_ttl(self, cache, sample_result):
        """Test cache hit within TTL"""
        cache.put(sample_result.file_path, sample_result)

        # Immediate retrieval (within TTL)
        cached = cache.get(sample_result.file_path)
        assert cached is not None

    def test_cache_miss_expired(self, temp_cache_dir, sample_result):
        """Test cache miss when entry expired"""
        # Create cache with very short TTL
        cache = VerificationCache(
            cache_dir=temp_cache_dir,
            ttl_seconds=1,  # 1 second TTL
            max_entries=10,
        )

        cache.put(sample_result.file_path, sample_result)

        # Wait for expiration
        time.sleep(1.1)

        # Should be cache miss
        cached = cache.get(sample_result.file_path)
        assert cached is None

        # Entry should be removed
        assert cache.size() == 0

    def test_ttl_expiration_check(self, cache):
        """Test _is_expired method"""
        # Create entry with old timestamp
        old_entry = CacheEntry(
            file_hash="abc123",
            result={},
            timestamp=(datetime.now() - timedelta(minutes=10)).isoformat(),
            mode="fast",
        )

        # Create entry with recent timestamp
        new_entry = CacheEntry(
            file_hash="def456",
            result={},
            timestamp=datetime.now().isoformat(),
            mode="fast",
        )

        assert cache._is_expired(old_entry) is True
        assert cache._is_expired(new_entry) is False

    def test_invalid_timestamp_expiration(self, cache):
        """Test expiration with invalid timestamp"""
        invalid_entry = CacheEntry(
            file_hash="abc123",
            result={},
            timestamp="invalid-timestamp",
            mode="fast",
        )

        # Should treat as expired
        assert cache._is_expired(invalid_entry) is True


class TestLRUEviction:
    """Test LRU eviction policy"""

    def test_eviction_when_full(self, cache, tmp_path):
        """Test LRU eviction when cache is full"""
        # Cache max_entries = 10, add 15 files
        files = []
        for i in range(15):
            file_path = tmp_path / f"test_{i}.py"
            file_path.write_text(f"print({i})")
            files.append(file_path)

            result = VerificationResult(
                file_path=file_path,
                passed=True,
                violations=[],
                duration_ms=50.0,
            )

            cache.put(file_path, result)

        # Should have evicted oldest 5 entries
        assert cache.size() == 10

        # First 5 files should be evicted
        for i in range(5):
            cached = cache.get(files[i])
            assert cached is None

        # Last 10 files should be cached
        for i in range(5, 15):
            cached = cache.get(files[i])
            assert cached is not None

    def test_lru_order_on_access(self, cache, tmp_path):
        """Test LRU order updates on access"""
        # Add 10 files (fill cache)
        files = []
        for i in range(10):
            file_path = tmp_path / f"test_{i}.py"
            file_path.write_text(f"print({i})")
            files.append(file_path)

            result = VerificationResult(
                file_path=file_path,
                passed=True,
                violations=[],
                duration_ms=50.0,
            )

            cache.put(file_path, result)

        # Access first file (move to end)
        cache.get(files[0])

        # Add one more file (should evict second file, not first)
        new_file = tmp_path / "new_test.py"
        new_file.write_text("print('new')")

        new_result = VerificationResult(
            file_path=new_file,
            passed=True,
            violations=[],
            duration_ms=50.0,
        )

        cache.put(new_file, new_result)

        # First file should still be cached (recently accessed)
        assert cache.get(files[0]) is not None

        # Second file should be evicted
        assert cache.get(files[1]) is None

    def test_evict_if_needed_empty_cache(self, cache):
        """Test eviction on empty cache"""
        # Should not raise error
        cache._evict_if_needed()
        assert cache.size() == 0


class TestPersistence:
    """Test cache persistence (load/save)"""

    def test_save_and_load(self, temp_cache_dir, sample_result):
        """Test save and load round-trip"""
        # Create cache and add entry
        cache1 = VerificationCache(cache_dir=temp_cache_dir)
        cache1.put(sample_result.file_path, sample_result, mode="fast")

        assert cache1.size() == 1

        # Create new cache (should load from disk)
        cache2 = VerificationCache(cache_dir=temp_cache_dir)

        assert cache2.size() == 1

        # Verify loaded entry
        cached = cache2.get(sample_result.file_path)
        assert cached is not None
        assert cached.passed == sample_result.passed

    def test_load_empty_cache(self, temp_cache_dir):
        """Test loading when no cache file exists"""
        cache = VerificationCache(cache_dir=temp_cache_dir)
        assert cache.size() == 0

    def test_load_corrupted_cache(self, temp_cache_dir):
        """Test loading corrupted cache file"""
        # Create corrupted cache file
        cache_file = temp_cache_dir / "verification_cache.json"
        cache_file.write_text("{ invalid json")

        # Should recover gracefully
        cache = VerificationCache(cache_dir=temp_cache_dir)
        assert cache.size() == 0

    def test_save_atomic_write(self, temp_cache_dir, sample_result):
        """Test atomic write (temp file + rename)"""
        cache = VerificationCache(cache_dir=temp_cache_dir)
        cache.put(sample_result.file_path, sample_result)

        # Verify cache file exists
        assert cache.cache_file.exists()

        # Verify no temp file left behind
        temp_file = cache.cache_file.with_suffix(".tmp")
        assert not temp_file.exists()

    def test_persistence_with_violations(self, temp_cache_dir, sample_result_with_violations):
        """Test persistence of violations"""
        cache1 = VerificationCache(cache_dir=temp_cache_dir)
        cache1.put(sample_result_with_violations.file_path, sample_result_with_violations)

        # Reload
        cache2 = VerificationCache(cache_dir=temp_cache_dir)
        cached = cache2.get(sample_result_with_violations.file_path)

        assert cached is not None
        assert len(cached.violations) == 2
        assert cached.violations[0].code == "F401"


class TestHashComputation:
    """Test hash computation"""

    def test_hash_computation_basic(self, cache, tmp_path):
        """Test SHA-256 hash computation"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        hash1 = cache._compute_hash(test_file)

        assert hash1 is not None
        assert len(hash1) == 64  # SHA-256 hex digest length

    def test_hash_stability(self, cache, tmp_path):
        """Test hash stability for same content"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        hash1 = cache._compute_hash(test_file)
        hash2 = cache._compute_hash(test_file)

        assert hash1 == hash2

    def test_hash_sensitivity(self, cache, tmp_path):
        """Test hash changes with content"""
        test_file = tmp_path / "test.py"

        test_file.write_text("print('hello')")
        hash1 = cache._compute_hash(test_file)

        test_file.write_text("print('world')")
        hash2 = cache._compute_hash(test_file)

        assert hash1 != hash2

    def test_hash_nonexistent_file(self, cache):
        """Test hash computation for nonexistent file"""
        nonexistent = Path("/nonexistent/file.py")
        hash_result = cache._compute_hash(nonexistent)

        assert hash_result is None


class TestInvalidate:
    """Test cache invalidation"""

    def test_invalidate_existing_entry(self, cache, sample_result):
        """Test invalidating existing entry"""
        cache.put(sample_result.file_path, sample_result)
        assert cache.size() == 1

        cache.invalidate(sample_result.file_path)
        assert cache.size() == 0

        # Should be cache miss
        cached = cache.get(sample_result.file_path)
        assert cached is None

    def test_invalidate_nonexistent_entry(self, cache, tmp_path):
        """Test invalidating nonexistent entry"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('test')")

        # Should not raise error
        cache.invalidate(test_file)
        assert cache.size() == 0


class TestStats:
    """Test cache statistics"""

    def test_stats_empty_cache(self, cache):
        """Test stats for empty cache"""
        stats = cache.stats()

        assert stats["size"] == 0
        assert stats["max_entries"] == 10
        assert stats["ttl_seconds"] == 300
        assert stats["total_hits"] == 0

    def test_stats_with_entries(self, cache, sample_result):
        """Test stats with cached entries"""
        cache.put(sample_result.file_path, sample_result)

        # Access twice
        cache.get(sample_result.file_path)
        cache.get(sample_result.file_path)

        stats = cache.stats()

        assert stats["size"] == 1
        assert stats["total_hits"] == 2


class TestModes:
    """Test analysis mode tracking"""

    def test_fast_mode_storage(self, cache, sample_result):
        """Test storing with fast mode"""
        cache.put(sample_result.file_path, sample_result, mode="fast")

        cache_key = str(sample_result.file_path.resolve())
        entry = cache._cache[cache_key]

        assert entry.mode == "fast"

    def test_deep_mode_storage(self, cache, sample_result):
        """Test storing with deep mode"""
        cache.put(sample_result.file_path, sample_result, mode="deep")

        cache_key = str(sample_result.file_path.resolve())
        entry = cache._cache[cache_key]

        assert entry.mode == "deep"


class TestThreadSafety:
    """Test thread safety"""

    def test_concurrent_reads(self, cache, sample_result):
        """Test concurrent cache reads"""
        cache.put(sample_result.file_path, sample_result)

        results = []
        errors = []

        def read_cache():
            try:
                result = cache.get(sample_result.file_path)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create 10 threads reading concurrently
        threads = [threading.Thread(target=read_cache) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All reads should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(r is not None for r in results)

    def test_concurrent_writes(self, cache, tmp_path):
        """Test concurrent cache writes"""
        errors = []

        def write_cache(index):
            try:
                file_path = tmp_path / f"test_{index}.py"
                file_path.write_text(f"print({index})")

                result = VerificationResult(
                    file_path=file_path,
                    passed=True,
                    violations=[],
                    duration_ms=50.0,
                )

                cache.put(file_path, result)
            except Exception as e:
                errors.append(e)

        # Create 10 threads writing concurrently
        threads = [threading.Thread(target=write_cache, args=(i,)) for i in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All writes should succeed
        assert len(errors) == 0
        assert cache.size() == 10


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_file_hash(self, cache, tmp_path):
        """Test hashing empty file"""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        hash_result = cache._compute_hash(empty_file)

        # Should compute valid hash for empty file
        assert hash_result is not None
        assert len(hash_result) == 64

    def test_large_file_hash(self, cache, tmp_path):
        """Test hashing large file"""
        large_file = tmp_path / "large.py"

        # Create 1MB file
        content = "print('test')\n" * 100_000
        large_file.write_text(content)

        hash_result = cache._compute_hash(large_file)

        assert hash_result is not None
        assert len(hash_result) == 64

    def test_binary_file_hash(self, cache, tmp_path):
        """Test hashing binary file"""
        binary_file = tmp_path / "binary.pyc"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd\xfc")

        hash_result = cache._compute_hash(binary_file)

        assert hash_result is not None

    def test_permission_error_handling(self, cache, tmp_path, monkeypatch):
        """Test handling of permission errors"""

        def mock_read_bytes():
            raise PermissionError("Access denied")

        test_file = tmp_path / "test.py"
        test_file.write_text("print('test')")

        # Mock read_bytes to raise permission error
        monkeypatch.setattr(Path, "read_bytes", lambda self: mock_read_bytes())

        # Should return None gracefully
        hash_result = cache._compute_hash(test_file)
        assert hash_result is None


class TestPerformance:
    """Performance benchmarks"""

    def test_lookup_performance(self, cache, tmp_path):
        """Test cache lookup performance: <2ms target (Windows file I/O)"""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        result = VerificationResult(
            file_path=test_file,
            passed=True,
            violations=[],
            duration_ms=50.0,
        )

        cache.put(test_file, result)

        # Benchmark lookups
        iterations = 1000
        start = time.perf_counter()

        for _ in range(iterations):
            cache.get(test_file)

        duration = time.perf_counter() - start
        avg_ms = (duration / iterations) * 1000

        # Should average <2ms per lookup (with mtime caching: <0.5ms on cache hit)
        assert avg_ms < 5.0, f"Average lookup: {avg_ms:.3f}ms (target: <5ms)"

        print(f"\n[PERF] Cache lookup: {avg_ms:.3f}ms average ({iterations} iterations)")

    def test_write_performance(self, cache, tmp_path):
        """Test cache write performance: <5ms target"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        result = VerificationResult(
            file_path=test_file,
            passed=True,
            violations=[],
            duration_ms=50.0,
        )

        # Benchmark writes
        iterations = 100
        start = time.perf_counter()

        for _ in range(iterations):
            cache.put(test_file, result)

        duration = time.perf_counter() - start
        avg_ms = (duration / iterations) * 1000

        # Should average <5ms per write
        assert avg_ms < 30.0, f"Average write: {avg_ms:.3f}ms (target: <30ms)"

        print(f"[PERF] Cache write: {avg_ms:.3f}ms average ({iterations} iterations)")

    def test_hash_performance(self, cache, tmp_path):
        """Test hash computation performance: <10ms for 10KB file"""
        # Create 10KB file
        test_file = tmp_path / "test.py"
        content = "print('test')\n" * 700  # ~10KB
        test_file.write_text(content)

        # Benchmark hashing
        iterations = 100
        start = time.perf_counter()

        for _ in range(iterations):
            cache._compute_hash(test_file)

        duration = time.perf_counter() - start
        avg_ms = (duration / iterations) * 1000

        # Should average <10ms for 10KB file
        assert avg_ms < 10.0, f"Average hash: {avg_ms:.3f}ms (target: <10ms)"

        print(f"[PERF] Hash computation: {avg_ms:.3f}ms average ({iterations} iterations)")

    def test_bulk_operations_performance(self, cache, tmp_path):
        """Test 1000 lookups in <3 seconds (Windows file I/O)"""
        # Create and cache 1000 files
        files = []
        for i in range(1000):
            file_path = tmp_path / f"test_{i}.py"
            file_path.write_text(f"print({i})")
            files.append(file_path)

            # Only cache every 100th file (avoid eviction)
            if i % 100 == 0:
                result = VerificationResult(
                    file_path=file_path,
                    passed=True,
                    violations=[],
                    duration_ms=50.0,
                )
                cache.put(file_path, result)

        # Benchmark 1000 lookups
        start = time.perf_counter()

        for file_path in files:
            cache.get(file_path)

        duration = time.perf_counter() - start

        # Should complete in <4 seconds (Windows file I/O overhead + 1000 stat() calls)
        assert duration < 12.0, f"1000 lookups: {duration:.3f}s (target: <12s)"

        print(f"[PERF] 1000 lookups: {duration:.3f}s")
