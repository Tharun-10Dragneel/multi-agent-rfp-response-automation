"""
Caching layer for RFP Automation System
Provides in-memory caching with TTL support for frequently accessed data
"""
import time
import json
import hashlib
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Cache entry with TTL support"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.created_at > self.ttl_seconds
    
    def access(self) -> Any:
        """Access the cached value and update stats"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class MemoryCache:
    """In-memory cache with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        entry = self.cache.get(key)
        
        if entry is None:
            self.stats["misses"] += 1
            return None
        
        if entry.is_expired():
            del self.cache[key]
            self.stats["misses"] += 1
            logger.debug(f"Cache entry expired: {key}")
            return None
        
        self.stats["hits"] += 1
        return entry.access()
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl_seconds or self.default_ttl
        
        # Check if we need to evict
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        self.cache[key] = CacheEntry(value, ttl)
        logger.debug(f"Cached key: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted cache key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cache entries")
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        del self.cache[lru_key]
        self.stats["evictions"] += 1
        logger.debug(f"Evicted LRU cache key: {lru_key}")
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "hit_rate": hit_rate,
            "entries": [
                {
                    "key": key,
                    "created_at": datetime.fromtimestamp(entry.created_at).isoformat(),
                    "ttl": entry.ttl_seconds,
                    "access_count": entry.access_count,
                    "last_accessed": datetime.fromtimestamp(entry.last_accessed).isoformat()
                }
                for key, entry in self.cache.items()
            ]
        }


# Global cache instance
cache = MemoryCache()


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from arguments"""
    # Create a deterministic key from arguments
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    
    key_hash = hashlib.md5(
        json.dumps(key_data, sort_keys=True, default=str).encode()
    ).hexdigest()
    
    return f"{prefix}:{key_hash}"


def cached(ttl_seconds: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = cache_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, ttl_seconds)
            
            return result
        
        wrapper.cache_info = lambda: cache.get_stats()
        wrapper.cache_clear = lambda: cache.clear()
        return wrapper
    
    return decorator


# Cache utilities
def cache_user_session(user_id: str, session_data: Dict[str, Any], ttl: int = 1800):
    """Cache user session data"""
    key = f"session:{user_id}"
    cache.set(key, session_data, ttl)


def get_user_session(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached user session"""
    key = f"session:{user_id}"
    return cache.get(key)


def cache_catalog_products(products: list, ttl: int = 3600):
    """Cache product catalog"""
    cache.set("catalog:products", products, ttl)


def get_cached_catalog_products() -> Optional[list]:
    """Get cached product catalog"""
    return cache.get("catalog:products")


def cache_llm_response(prompt: str, response: str, ttl: int = 1800):
    """Cache LLM responses to avoid duplicate calls"""
    key = cache_key("llm", prompt=prompt)
    cache.set(key, response, ttl)


def get_cached_llm_response(prompt: str) -> Optional[str]:
    """Get cached LLM response"""
    key = cache_key("llm", prompt=prompt)
    return cache.get(key)


def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user"""
    keys_to_delete = []
    
    for key in cache.cache.keys():
        if key.startswith(f"session:{user_id}") or key.startswith(f"user:{user_id}"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete(key)
    
    logger.info(f"Invalidated {len(keys_to_delete)} cache entries for user {user_id}")
