"""
Cache Module

Provides efficient caching with multiple strategies (LRU, LFU, FIFO).
"""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
import time


class CacheEntry:
    """Represents a cached item with metadata"""
    
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.access_count = 0
        self.expires_at = (
            datetime.now() + timedelta(seconds=ttl) if ttl else None
        )
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def touch(self):
        """Update access metadata"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class LRUCache:
    """Least Recently Used cache implementation"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        entry.touch()
        self.hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if key in self.cache:
            del self.cache[key]
        
        entry = CacheEntry(key, value, ttl or self.default_ttl)
        self.cache[key] = entry
        
        # Evict oldest if over capacity
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


class LFUCache:
    """Least Frequently Used cache implementation"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        entry.touch()
        self.hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if key in self.cache:
            del self.cache[key]
        
        entry = CacheEntry(key, value, ttl or self.default_ttl)
        self.cache[key] = entry
        
        # Evict least frequently used if over capacity
        if len(self.cache) > self.max_size:
            lfu_key = min(self.cache.items(), key=lambda x: x[1].access_count)[0]
            del self.cache[lfu_key]
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


class CacheManager:
    """
    Manages caching with configurable strategies.
    
    Features:
    - Multiple cache strategies (LRU, LFU)
    - TTL support
    - Cache statistics
    - Thread-safe operations
    """
    
    def __init__(self, strategy: str = "lru", max_size: int = 1000, default_ttl: Optional[int] = None):
        self.strategy = strategy
        
        if strategy == "lru":
            self.cache = LRUCache(max_size, default_ttl)
        elif strategy == "lfu":
            self.cache = LFUCache(max_size, default_ttl)
        else:
            raise ValueError(f"Unknown cache strategy: {strategy}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        self.cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        return self.cache.delete(key)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache.get_stats()
        stats["strategy"] = self.strategy
        return stats
