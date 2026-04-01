"""
In-memory cache for stream URLs with expiration handling
"""

import time
import hashlib
from typing import Optional, Dict, Any, List
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class CachedStreamData:
    """Represents cached stream data with expiration"""
    
    def __init__(self, data: Dict[str, Any], ttl_seconds: int = 3600):
        """
        Initialize cached stream data
        
        Args:
            data: Stream data to cache
            ttl_seconds: Time-to-live in seconds (default 1 hour)
        """
        self.data = data
        self.created_at = int(time.time())
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        current_time = int(time.time())
        age = current_time - self.created_at
        expired = age >= self.ttl_seconds
        
        if expired:
            logger.debug(f"Cache entry expired: age={age}s, ttl={self.ttl_seconds}s")
        
        return expired
    
    def get_remaining_ttl(self) -> int:
        """Get remaining time-to-live in seconds"""
        current_time = int(time.time())
        age = current_time - self.created_at
        remaining = max(0, self.ttl_seconds - age)
        return remaining


class StreamCache:
    """
    In-memory cache for stream URLs with expiration handling
    
    Cache key structure:
    - For movies: f"movie:{slug}:{subject_id}"
    - For TV episodes: f"episode:{slug}:{subject_id}:{season}:{episode}"
    """
    
    def __init__(self, default_ttl_seconds: int = 3600):
        """
        Initialize stream cache
        
        Args:
            default_ttl_seconds: Default time-to-live for cache entries
        """
        self._cache: Dict[str, CachedStreamData] = {}
        self._lock = Lock()
        self.default_ttl_seconds = default_ttl_seconds
    
    @staticmethod
    def _generate_key(cache_type: str, slug: str, subject_id: str, 
                      season: Optional[int] = None, episode: Optional[int] = None) -> str:
        """
        Generate cache key
        
        Args:
            cache_type: 'movie' or 'episode'
            slug: Content slug
            subject_id: Subject ID
            season: Season number (for episodes)
            episode: Episode number (for episodes)
            
        Returns:
            Cache key string
        """
        if cache_type == 'movie':
            return f"movie:{slug}:{subject_id}"
        elif cache_type == 'episode':
            if season is None or episode is None:
                raise ValueError("season and episode are required for episode cache keys")
            return f"episode:{slug}:{subject_id}:{season}:{episode}"
        else:
            raise ValueError(f"Invalid cache_type: {cache_type}")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached stream data
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            cached = self._cache[key]
            
            if cached.is_expired():
                logger.debug(f"Cache entry expired, removing: {key}")
                del self._cache[key]
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return cached.data
    
    def set(self, key: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None):
        """
        Store stream data in cache
        
        Args:
            key: Cache key
            data: Stream data to cache
            ttl_seconds: Time-to-live (uses default if None)
        """
        with self._lock:
            ttl = ttl_seconds or self.default_ttl_seconds
            cached = CachedStreamData(data, ttl)
            self._cache[key] = cached
            logger.info(f"Cached stream data for key: {key}, ttl={ttl}s")
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            True if entry was removed, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Invalidated cache entry: {key}")
                return True
            logger.debug(f"Cache entry not found for invalidation: {key}")
            return False
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate multiple cache entries by pattern
        
        Args:
            pattern: Pattern to match (supports simple wildcards)
            Example: "episode:xyz:12345*" to invalidate all episodes of a show
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            import re
            
            # Convert simple pattern to regex
            # e.g., "movie:*:123" -> r"^movie:.*:123$"
            regex_pattern = pattern.replace("*", ".*")
            regex_pattern = f"^{regex_pattern}$"
            
            regex = re.compile(regex_pattern)
            keys_to_remove = [k for k in self._cache.keys() if regex.match(k)]
            
            for key in keys_to_remove:
                del self._cache[key]
            
            if keys_to_remove:
                logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
            
            return len(keys_to_remove)
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared cache ({count} entries)")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache statistics
        """
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for c in self._cache.values() if c.is_expired())
            active_entries = total_entries - expired_entries
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": expired_entries,
                "cache_keys": list(self._cache.keys())
            }


# Global cache instance
_global_stream_cache = StreamCache(default_ttl_seconds=3600)  # 1 hour default TTL


def get_stream_cache() -> StreamCache:
    """Get global stream cache instance"""
    return _global_stream_cache
