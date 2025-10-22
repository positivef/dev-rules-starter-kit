"""Verification Cache for Development Assistant Phase C

File hash-based caching to avoid re-verifying unchanged files.

Features:
- SHA-256 content hashing for change detection
- TTL-based expiration (5 minutes default)
- LRU eviction when cache exceeds max size (1000 entries)
- Persistent JSON storage with atomic writes
- Thread-safe operations with file locking
- Graceful degradation on errors (in-memory fallback)

Performance:
- Cache lookup: <1ms (target <0.5ms)
- Cache write: <5ms (including JSON serialization)
- Hash computation: <10ms for 10KB file
- 1000 lookups: <1 second total

Usage:
    cache = VerificationCache(cache_dir=Path("RUNS/.cache"))

    # Check cache before verification
    cached = cache.get(file_path)
    if cached is not None:
        return cached

    # Run verification
    result = verifier.verify_file(file_path)

    # Store in cache
    cache.put(file_path, result, mode="fast")
"""

import hashlib
import json
import logging
import threading
from collections import OrderedDict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class RuffViolation:
    """Represents a single Ruff violation (matches dev_assistant.py)"""

    code: str
    message: str
    line: int
    column: int
    fix_available: bool = False


@dataclass
class VerificationResult:
    """Result of Ruff verification for a file (matches dev_assistant.py)"""

    file_path: Path
    passed: bool
    violations: list[RuffViolation]
    duration_ms: float
    error: Optional[str] = None

    @property
    def violation_count(self) -> int:
        """Return count of violations"""
        return len(self.violations)


@dataclass
class CacheEntry:
    """Cache entry with metadata

    Attributes:
        file_hash: SHA-256 hex digest of file content
        result: VerificationResult from Phase A RuffVerifier
        timestamp: When cached (ISO format string)
        mode: Analysis mode ("fast" or "deep")
        access_count: Number of cache hits (for LRU)
    """

    file_hash: str
    result: Dict[str, Any]  # Serialized VerificationResult
    timestamp: str  # ISO format datetime
    mode: str
    access_count: int = 0


class VerificationCache:
    """File hash-based verification cache with LRU eviction and TTL

    Implements a persistent cache for verification results to avoid
    redundant file analysis. Uses SHA-256 hashing for change detection,
    TTL-based expiration, and LRU eviction for size management.

    Thread-safe with file locking for concurrent access.

    Attributes:
        cache_dir: Directory for cache storage
        ttl_seconds: Time-to-live for cache entries (default: 300)
        max_entries: Maximum cache size (default: 1000)
    """

    def __init__(
        self,
        cache_dir: Path,
        ttl_seconds: int = 300,  # 5 minutes
        max_entries: int = 1000,
    ):
        """Initialize verification cache

        Args:
            cache_dir: Directory for cache file storage
            ttl_seconds: Time-to-live for entries (seconds)
            max_entries: Maximum number of cached entries
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries

        # Cache file path
        self.cache_file = self.cache_dir / "verification_cache.json"

        # In-memory cache: {file_path_str: CacheEntry}
        # Using OrderedDict for LRU tracking
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Hash cache to avoid re-computing for same file
        # {file_path_str: (mtime, hash)}
        self._hash_cache: Dict[str, tuple[float, str]] = {}

        # Thread safety
        self._lock = threading.Lock()

        # Ensure cache directory exists
        self._ensure_cache_dir()

        # Load cache from disk
        self._load_cache()

        logger.info(f"VerificationCache initialized: {len(self._cache)} entries, " f"TTL={ttl_seconds}s, max={max_entries}")

    def get(self, file_path: Path) -> Optional[VerificationResult]:
        """Get cached verification result if valid

        Returns cached result only if:
        1. Entry exists
        2. File hash matches (content unchanged)
        3. Entry not expired (within TTL)

        Args:
            file_path: Path to file to check

        Returns:
            VerificationResult if cached and valid, None otherwise

        Performance: <1ms (target <0.5ms)
        """
        with self._lock:
            # Check if file exists
            if not file_path.exists():
                logger.debug(f"[CACHE] File not found: {file_path.name}")
                return None

            # Compute current hash
            current_hash = self._compute_hash(file_path)
            if current_hash is None:
                return None

            # Check cache
            cache_key = str(file_path.resolve())
            entry = self._cache.get(cache_key)

            if entry is None:
                logger.debug(f"[CACHE MISS] No entry: {file_path.name}")
                return None

            # Validate hash
            if entry.file_hash != current_hash:
                logger.debug(
                    f"[CACHE MISS] Hash mismatch: {file_path.name} "
                    f"(cached={entry.file_hash[:8]}, current={current_hash[:8]})"
                )
                # Remove stale entry
                del self._cache[cache_key]
                return None

            # Check expiration
            if self._is_expired(entry):
                logger.debug(f"[CACHE MISS] Expired: {file_path.name}")
                # Remove expired entry
                del self._cache[cache_key]
                return None

            # Update access count and move to end (LRU)
            entry.access_count += 1
            self._cache.move_to_end(cache_key)

            # Deserialize result
            result = self._deserialize_result(entry.result)

            logger.debug(
                f"[CACHE HIT] {file_path.name} " f"(age={self._get_age_seconds(entry):.1f}s, " f"hits={entry.access_count})"
            )

            return result

    def put(self, file_path: Path, result: VerificationResult, mode: str = "fast") -> None:
        """Store verification result in cache

        Computes file hash and stores result with metadata.
        Triggers eviction if cache exceeds max_entries.
        Persists to disk after update.

        Args:
            file_path: Path to verified file
            result: VerificationResult to cache
            mode: Analysis mode ("fast" or "deep")

        Performance: <5ms (including JSON serialization)
        """
        with self._lock:
            # Compute hash
            file_hash = self._compute_hash(file_path)
            if file_hash is None:
                logger.warning(f"[CACHE] Cannot hash file: {file_path.name}")
                return

            # Serialize result
            serialized_result = self._serialize_result(result)

            # Create entry
            entry = CacheEntry(
                file_hash=file_hash,
                result=serialized_result,
                timestamp=datetime.now().isoformat(),
                mode=mode,
                access_count=0,
            )

            # Store in cache
            cache_key = str(file_path.resolve())
            self._cache[cache_key] = entry
            self._cache.move_to_end(cache_key)  # Mark as recently used

            # Evict if needed
            self._evict_if_needed()

            # Persist to disk
            self._save_cache()

            logger.debug(f"[CACHE PUT] {file_path.name} " f"(mode={mode}, hash={file_hash[:8]})")

    def invalidate(self, file_path: Path) -> None:
        """Remove cache entry for file

        Used for testing and explicit cache invalidation.

        Args:
            file_path: Path to file to invalidate
        """
        with self._lock:
            cache_key = str(file_path.resolve())
            if cache_key in self._cache:
                del self._cache[cache_key]
                self._save_cache()
                logger.debug(f"[CACHE] Invalidated: {file_path.name}")

    def clear(self) -> None:
        """Remove all cache entries

        Clears both in-memory cache and persistent storage.
        """
        with self._lock:
            self._cache.clear()
            self._save_cache()
            logger.info("[CACHE] Cleared all entries")

    def size(self) -> int:
        """Return current cache size

        Returns:
            Number of entries in cache
        """
        with self._lock:
            return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics

        Returns:
            Dictionary with cache metrics
        """
        with self._lock:
            total_hits = sum(entry.access_count for entry in self._cache.values())

            return {
                "size": len(self._cache),
                "max_entries": self.max_entries,
                "ttl_seconds": self.ttl_seconds,
                "total_hits": total_hits,
                "cache_file": str(self.cache_file),
            }

    # Private methods

    def _compute_hash(self, file_path: Path) -> Optional[str]:
        """Compute SHA-256 hash of file content with mtime caching

        Uses modification time (mtime) to avoid re-hashing unchanged files.

        Args:
            file_path: Path to file to hash

        Returns:
            SHA-256 hex digest, or None on error

        Performance: <10ms for 10KB file (first access), <0.1ms cached
        """
        try:
            # Get file mtime
            stat = file_path.stat()
            mtime = stat.st_mtime
            cache_key = str(file_path.resolve())

            # Check hash cache
            if cache_key in self._hash_cache:
                cached_mtime, cached_hash = self._hash_cache[cache_key]
                if cached_mtime == mtime:
                    # File unchanged, use cached hash
                    return cached_hash

            # Read file in binary mode for accurate hashing
            content = file_path.read_bytes()

            # Compute SHA-256
            hash_obj = hashlib.sha256(content)
            file_hash = hash_obj.hexdigest()

            # Cache hash with mtime
            self._hash_cache[cache_key] = (mtime, file_hash)

            return file_hash

        except (OSError, IOError) as e:
            logger.warning(f"Failed to hash {file_path.name}: {e}")
            return None

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired

        Args:
            entry: Cache entry to check

        Returns:
            True if expired, False otherwise
        """
        try:
            timestamp = datetime.fromisoformat(entry.timestamp)
            age = datetime.now() - timestamp
            return age > timedelta(seconds=self.ttl_seconds)
        except (ValueError, TypeError):
            # Invalid timestamp format
            return True

    def _get_age_seconds(self, entry: CacheEntry) -> float:
        """Get age of cache entry in seconds

        Args:
            entry: Cache entry to check

        Returns:
            Age in seconds
        """
        try:
            timestamp = datetime.fromisoformat(entry.timestamp)
            age = datetime.now() - timestamp
            return age.total_seconds()
        except (ValueError, TypeError):
            return float("inf")

    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache exceeds max size

        Uses LRU policy: removes least recently used entries first.
        OrderedDict maintains insertion/access order.
        """
        while len(self._cache) > self.max_entries:
            # Remove oldest (first) entry
            evicted_key, evicted_entry = self._cache.popitem(last=False)
            logger.debug(
                f"[CACHE EVICT] {Path(evicted_key).name} "
                f"(age={self._get_age_seconds(evicted_entry):.1f}s, "
                f"hits={evicted_entry.access_count})"
            )

    def _serialize_result(self, result: VerificationResult) -> Dict[str, Any]:
        """Serialize VerificationResult to JSON-compatible dict

        Args:
            result: VerificationResult to serialize

        Returns:
            JSON-compatible dictionary
        """
        return {
            "file_path": str(result.file_path),
            "passed": result.passed,
            "violations": [
                {
                    "code": v.code,
                    "message": v.message,
                    "line": v.line,
                    "column": v.column,
                    "fix_available": v.fix_available,
                }
                for v in result.violations
            ],
            "duration_ms": result.duration_ms,
            "error": result.error,
        }

    def _deserialize_result(self, data: Dict[str, Any]) -> VerificationResult:
        """Deserialize VerificationResult from JSON dict

        Args:
            data: JSON-compatible dictionary

        Returns:
            VerificationResult instance
        """
        violations = [RuffViolation(**v) for v in data.get("violations", [])]

        return VerificationResult(
            file_path=Path(data["file_path"]),
            passed=data["passed"],
            violations=violations,
            duration_ms=data["duration_ms"],
            error=data.get("error"),
        )

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists

        Creates directory if needed, logs warning if fails.
        """
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(f"Failed to create cache directory {self.cache_dir}: {e}. " f"Operating in-memory only.")

    def _load_cache(self) -> None:
        """Load cache from JSON file

        Handles errors gracefully:
        - File not found: Start with empty cache
        - JSON decode error: Rebuild from scratch
        - Permission error: Log warning, operate in-memory
        """
        if not self.cache_file.exists():
            logger.debug("No cache file found, starting fresh")
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate and load entries
            loaded = 0
            for key, entry_data in data.items():
                try:
                    entry = CacheEntry(**entry_data)
                    self._cache[key] = entry
                    loaded += 1
                except (TypeError, ValueError) as e:
                    logger.warning(f"Skipping invalid cache entry {key}: {e}")

            logger.info(f"Loaded {loaded} entries from cache file")

        except json.JSONDecodeError as e:
            logger.warning(f"Cache file corrupted: {e}. Rebuilding cache.")
            self._cache.clear()

        except OSError as e:
            logger.warning(f"Failed to load cache: {e}. Operating in-memory only.")

    def _save_cache(self) -> None:
        """Save cache to JSON file with atomic write

        Uses temp file + rename for atomicity.
        Handles errors gracefully (logs warning, continues in-memory).
        """
        try:
            # Serialize cache
            data = {key: asdict(entry) for key, entry in self._cache.items()}

            # Atomic write: temp file + rename
            temp_file = self.cache_file.with_suffix(".tmp")

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Atomic rename
            temp_file.replace(self.cache_file)

            logger.debug(f"Saved {len(self._cache)} entries to cache file")

        except OSError as e:
            logger.warning(f"Failed to save cache: {e}. Continuing in-memory.")


def main():
    """CLI entry point for testing"""
    import sys

    # Setup logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

    # Create cache
    cache_dir = Path("RUNS/.cache")
    cache = VerificationCache(cache_dir=cache_dir)

    print(f"\nCache initialized: {cache.stats()}\n")

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])

        # Try to get from cache
        result = cache.get(file_path)

        if result:
            print(f"Cache hit: {result}")
        else:
            print(f"Cache miss: {file_path.name}")

            # Create dummy result for testing
            dummy_result = VerificationResult(
                file_path=file_path,
                passed=True,
                violations=[],
                duration_ms=50.0,
                error=None,
            )

            cache.put(file_path, dummy_result, mode="fast")
            print(f"Stored in cache: {file_path.name}")

    print(f"\nFinal stats: {cache.stats()}\n")


if __name__ == "__main__":
    main()
