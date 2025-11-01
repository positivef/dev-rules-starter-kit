"""Smart Cache Manager - Only cache what matters.

This solves the over-caching problem. Instead of caching everything,
we only cache configuration files and frequently accessed data.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class SmartCacheManager:
    """Intelligent caching based on file type and access patterns."""

    # What to cache (high-value, slow-changing)
    CACHE_WORTHY = {
        ".yaml",
        ".yml",  # Config files
        ".json",  # Config and data
        ".toml",  # Config files
        ".ini",  # Config files
        ".env",  # Environment config
    }

    # What NOT to cache (frequently changing or large)
    NEVER_CACHE = {
        ".log",  # Always changing
        ".tmp",  # Temporary files
        ".pyc",  # Compiled files
        ".cache",  # Cache files themselves
        ".db",  # Database files (too large)
        ".sqlite",  # Database files
    }

    # Cache time limits (seconds)
    CACHE_DURATION = {
        "config": 300,  # 5 minutes for config files
        "data": 60,  # 1 minute for data files
        "default": 30,  # 30 seconds for everything else
    }

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize smart cache manager.

        Args:
            cache_dir: Directory for cache storage.
        """
        self.cache_dir = cache_dir or Path(".smart_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = self.cache_dir / "index.json"
        self.cache_index = self._load_index()
        self.access_count: Dict[str, int] = {}

    def _load_index(self) -> Dict[str, Dict]:
        """Load cache index from disk.

        Returns:
            Cache index dictionary.
        """
        if self.cache_index_file.exists():
            with open(self.cache_index_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        # Clean expired entries first
        self._cleanup_expired()

        with open(self.cache_index_file, "w", encoding="utf-8") as f:
            json.dump(self.cache_index, f, indent=2)

    def should_cache(self, file_path: Path) -> bool:
        """Determine if a file should be cached.

        Args:
            file_path: Path to file.

        Returns:
            True if file should be cached.
        """
        # Check file extension
        suffix = file_path.suffix.lower()

        # Never cache certain types
        if suffix in self.NEVER_CACHE:
            return False

        # Always cache config files
        if suffix in self.CACHE_WORTHY:
            return True

        # Check file size (don't cache large files)
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > 1:  # Don't cache files > 1MB
                return False

        # Check access frequency
        access_key = str(file_path)
        self.access_count[access_key] = self.access_count.get(access_key, 0) + 1

        # Cache if accessed more than 3 times
        return self.access_count[access_key] > 3

    def get_cache_duration(self, file_path: Path) -> int:
        """Get appropriate cache duration for a file.

        Args:
            file_path: Path to file.

        Returns:
            Cache duration in seconds.
        """
        suffix = file_path.suffix.lower()

        # Config files get longer cache
        if suffix in {".yaml", ".yml", ".json", ".toml", ".ini"}:
            return self.CACHE_DURATION["config"]

        # Data files get shorter cache
        if suffix in {".csv", ".txt"}:
            return self.CACHE_DURATION["data"]

        return self.CACHE_DURATION["default"]

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if valid.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        if key not in self.cache_index:
            return None

        entry = self.cache_index[key]

        # Check expiration
        if time.time() > entry["expires"]:
            # Expired - remove from cache
            del self.cache_index[key]
            cache_file = self.cache_dir / entry["file"]
            if cache_file.exists():
                cache_file.unlink()
            return None

        # Load cached data
        cache_file = self.cache_dir / entry["file"]
        if not cache_file.exists():
            # Cache file missing - remove from index
            del self.cache_index[key]
            return None

        try:
            with open(cache_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Corrupted cache - remove
            del self.cache_index[key]
            cache_file.unlink()
            return None

    def set(self, key: str, value: Any, duration: Optional[int] = None) -> bool:
        """Store value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            duration: Cache duration in seconds (optional).

        Returns:
            True if successfully cached.
        """
        # Generate cache file name
        hash_key = hashlib.md5(key.encode()).hexdigest()[:8]
        cache_file = self.cache_dir / f"{hash_key}.json"

        # Determine duration
        if duration is None:
            path = Path(key)
            if path.exists():
                duration = self.get_cache_duration(path)
            else:
                duration = self.CACHE_DURATION["default"]

        # Store data
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(value, f)

            # Update index
            self.cache_index[key] = {
                "file": cache_file.name,
                "expires": time.time() + duration,
                "size": cache_file.stat().st_size,
            }

            self._save_index()
            return True

        except Exception as e:
            print(f"[WARN] Failed to cache {key}: {e}")
            return False

    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Pattern to match (e.g., "config/*").

        Returns:
            Number of entries invalidated.
        """
        import fnmatch

        count = 0
        keys_to_remove = []

        for key in self.cache_index:
            if fnmatch.fnmatch(key, pattern):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            entry = self.cache_index[key]
            cache_file = self.cache_dir / entry["file"]
            if cache_file.exists():
                cache_file.unlink()
            del self.cache_index[key]
            count += 1

        if count > 0:
            self._save_index()

        return count

    def _cleanup_expired(self) -> int:
        """Remove expired cache entries.

        Returns:
            Number of entries removed.
        """
        current_time = time.time()
        expired_keys = []

        for key, entry in self.cache_index.items():
            if current_time > entry["expires"]:
                expired_keys.append(key)

        for key in expired_keys:
            entry = self.cache_index[key]
            cache_file = self.cache_dir / entry["file"]
            if cache_file.exists():
                cache_file.unlink()
            del self.cache_index[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary of cache stats.
        """
        total_size = 0
        file_types: Dict[str, int] = {}

        for entry in self.cache_index.values():
            total_size += entry.get("size", 0)

        for key in self.cache_index:
            path = Path(key)
            suffix = path.suffix.lower()
            file_types[suffix] = file_types.get(suffix, 0) + 1

        # Calculate cache directory size
        cache_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))

        return {
            "entries": len(self.cache_index),
            "total_size_bytes": total_size,
            "cache_dir_size_bytes": cache_size,
            "file_types": file_types,
            "expired_cleaned": self._cleanup_expired(),
            "access_patterns": dict(
                sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)[:10]
            ),  # Top 10 accessed files
        }

    def optimize(self) -> Dict[str, Any]:
        """Optimize cache based on usage patterns.

        Returns:
            Optimization results.
        """
        stats_before = self.get_stats()

        # Remove expired entries
        expired = self._cleanup_expired()

        # Remove rarely accessed entries
        rarely_accessed = []
        for key in list(self.cache_index.keys()):
            if self.access_count.get(key, 0) < 2:
                entry = self.cache_index[key]
                cache_file = self.cache_dir / entry["file"]
                if cache_file.exists():
                    cache_file.unlink()
                del self.cache_index[key]
                rarely_accessed.append(key)

        # Remove oversized cache files
        oversized = []
        for key, entry in list(self.cache_index.items()):
            if entry.get("size", 0) > 100_000:  # 100KB limit
                cache_file = self.cache_dir / entry["file"]
                if cache_file.exists():
                    cache_file.unlink()
                del self.cache_index[key]
                oversized.append(key)

        self._save_index()
        stats_after = self.get_stats()

        return {
            "expired_removed": expired,
            "rarely_accessed_removed": len(rarely_accessed),
            "oversized_removed": len(oversized),
            "size_before": stats_before["cache_dir_size_bytes"],
            "size_after": stats_after["cache_dir_size_bytes"],
            "size_saved": stats_before["cache_dir_size_bytes"] - stats_after["cache_dir_size_bytes"],
        }


def main():
    """Demo smart caching."""
    print("\n" + "=" * 60)
    print("Smart Cache Manager Demo")
    print("=" * 60)

    cache = SmartCacheManager()

    # Show what would be cached
    test_files = [
        Path("config/settings.yaml"),
        Path("data/large_file.db"),
        Path("logs/app.log"),
        Path("scripts/test.py"),
        Path("config/feature_flags.json"),
    ]

    print("\n[INFO] Cache Decisions:")
    for file in test_files:
        should = cache.should_cache(file)
        duration = cache.get_cache_duration(file) if should else 0
        print(f"  {file}: {'CACHE' if should else 'SKIP'} " f"({duration}s)" if should else "")

    # Simulate some caching
    cache.set("config/settings.yaml", {"debug": True}, 300)
    cache.set("config/feature_flags.json", {"feature_x": False}, 300)

    # Show stats
    stats = cache.get_stats()
    print("\n[INFO] Cache Statistics:")
    print(f"  Entries: {stats['entries']}")
    print(f"  Size: {stats['cache_dir_size_bytes']} bytes")
    print(f"  File types: {stats['file_types']}")

    # Optimize
    print("\n[INFO] Optimizing cache...")
    results = cache.optimize()
    print(f"  Expired removed: {results['expired_removed']}")
    print(f"  Rarely accessed removed: {results['rarely_accessed_removed']}")
    print(f"  Size saved: {results['size_saved']} bytes")


if __name__ == "__main__":
    main()
