"""
Unit tests for the Cache Manager module.
"""

import unittest
from cache_manager import CacheManager, LRUCache, LFUCache


class TestLRUCache(unittest.TestCase):
    """Test cases for LRU Cache"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = LRUCache(max_size=3)
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        self.cache.set("key1", "value1")
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
    
    def test_get_nonexistent(self):
        """Test getting non-existent key"""
        value = self.cache.get("nonexistent")
        self.assertIsNone(value)
    
    def test_eviction(self):
        """Test LRU eviction"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        self.cache.set("key4", "value4")  # Should evict key1
        
        value = self.cache.get("key1")
        self.assertIsNone(value)
        
        value = self.cache.get("key2")
        self.assertEqual(value, "value2")
    
    def test_lru_ordering(self):
        """Test LRU ordering after access"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key1 to make it most recently used
        self.cache.get("key1")
        
        # Add key4, should evict key2 (least recently used)
        self.cache.set("key4", "value4")
        
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key1"))
    
    def test_delete(self):
        """Test deleting values"""
        self.cache.set("key1", "value1")
        result = self.cache.delete("key1")
        
        self.assertTrue(result)
        self.assertIsNone(self.cache.get("key1"))
    
    def test_clear(self):
        """Test clearing cache"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_stats(self):
        """Test cache statistics"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["total_requests"], 2)


class TestLFUCache(unittest.TestCase):
    """Test cases for LFU Cache"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = LFUCache(max_size=3)
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        self.cache.set("key1", "value1")
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
    
    def test_lfu_eviction(self):
        """Test LFU eviction"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key2 and key3 multiple times
        self.cache.get("key2")
        self.cache.get("key2")
        self.cache.get("key3")
        
        # Add key4, should evict key1 (least frequently used)
        self.cache.set("key4", "value4")
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key2"))
    
    def test_stats(self):
        """Test cache statistics"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)


class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager"""
    
    def test_lru_strategy(self):
        """Test LRU strategy initialization"""
        manager = CacheManager(strategy="lru", max_size=10)
        manager.set("key1", "value1")
        value = manager.get("key1")
        
        self.assertEqual(value, "value1")
    
    def test_lfu_strategy(self):
        """Test LFU strategy initialization"""
        manager = CacheManager(strategy="lfu", max_size=10)
        manager.set("key1", "value1")
        value = manager.get("key1")
        
        self.assertEqual(value, "value1")
    
    def test_invalid_strategy(self):
        """Test invalid strategy raises error with supported options"""
        with self.assertRaises(ValueError) as ctx:
            CacheManager(strategy="invalid")
        self.assertIn("Supported strategies", str(ctx.exception))
    
    def test_get_stats_with_strategy(self):
        """Test getting stats includes strategy"""
        manager = CacheManager(strategy="lru")
        stats = manager.get_stats()
        
        self.assertEqual(stats["strategy"], "lru")


if __name__ == "__main__":
    unittest.main()
