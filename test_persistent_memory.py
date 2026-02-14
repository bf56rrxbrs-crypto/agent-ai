"""
Unit tests for the Persistent Memory module.
"""

import unittest
import os
import json
import tempfile
from persistent_memory import PersistentMemory, Memory


class TestMemory(unittest.TestCase):
    """Test cases for Memory dataclass"""

    def test_memory_creation(self):
        """Test creating a memory entry"""
        mem = Memory(
            memory_id="test-001",
            category="general",
            content="Test memory content",
        )
        self.assertEqual(mem.memory_id, "test-001")
        self.assertEqual(mem.category, "general")
        self.assertEqual(mem.content, "Test memory content")
        self.assertEqual(mem.access_count, 0)
        self.assertFalse(mem.is_expired())

    def test_memory_touch(self):
        """Test updating access metadata"""
        mem = Memory(
            memory_id="test-002",
            category="general",
            content="Test",
        )
        initial_access = mem.last_accessed
        mem.touch()
        self.assertEqual(mem.access_count, 1)

    def test_memory_serialization(self):
        """Test Memory to_dict and from_dict"""
        mem = Memory(
            memory_id="test-003",
            category="test",
            content="Serialization test",
            importance=0.8,
            metadata={"key": "value"},
        )
        data = mem.to_dict()
        restored = Memory.from_dict(data)
        self.assertEqual(restored.memory_id, mem.memory_id)
        self.assertEqual(restored.content, mem.content)
        self.assertEqual(restored.importance, mem.importance)

    def test_memory_expiration(self):
        """Test TTL-based memory expiration"""
        mem = Memory(
            memory_id="test-004",
            category="general",
            content="Short-lived",
            expires_at="2000-01-01T00:00:00",  # Already expired
        )
        self.assertTrue(mem.is_expired())

    def test_memory_no_expiration(self):
        """Test memory without TTL never expires"""
        mem = Memory(
            memory_id="test-005",
            category="general",
            content="Permanent",
        )
        self.assertFalse(mem.is_expired())


class TestPersistentMemory(unittest.TestCase):
    """Test cases for PersistentMemory"""

    def setUp(self):
        """Set up test fixtures with a temporary storage file"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "test_memory.json")
        self.memory = PersistentMemory(
            storage_path=self.storage_path, max_memories=10
        )

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_store_and_recall(self):
        """Test storing and recalling a memory"""
        mid = self.memory.store("Test content", category="test")
        recalled = self.memory.recall(mid)
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.content, "Test content")
        self.assertEqual(recalled.category, "test")

    def test_store_with_importance(self):
        """Test storing with custom importance"""
        mid = self.memory.store("Important memory", importance=0.9)
        recalled = self.memory.recall(mid)
        self.assertEqual(recalled.importance, 0.9)

    def test_importance_clamping(self):
        """Test importance is clamped to [0.0, 1.0]"""
        mid1 = self.memory.store("Over", importance=1.5)
        mid2 = self.memory.store("Under", importance=-0.5)
        self.assertEqual(self.memory.recall(mid1).importance, 1.0)
        self.assertEqual(self.memory.recall(mid2).importance, 0.0)

    def test_recall_nonexistent(self):
        """Test recalling non-existent memory"""
        result = self.memory.recall("nonexistent")
        self.assertIsNone(result)

    def test_recall_by_category(self):
        """Test recalling memories by category"""
        self.memory.store("Memory A", category="work")
        self.memory.store("Memory B", category="work")
        self.memory.store("Memory C", category="personal")

        work_memories = self.memory.recall_by_category("work")
        self.assertEqual(len(work_memories), 2)

        personal_memories = self.memory.recall_by_category("personal")
        self.assertEqual(len(personal_memories), 1)

    def test_search(self):
        """Test keyword search"""
        self.memory.store("Python programming tips")
        self.memory.store("JavaScript frameworks")
        self.memory.store("Python data analysis")

        results = self.memory.search("python")
        self.assertEqual(len(results), 2)

    def test_search_case_insensitive(self):
        """Test search is case-insensitive"""
        self.memory.store("UPPERCASE content")
        results = self.memory.search("uppercase")
        self.assertEqual(len(results), 1)

    def test_forget(self):
        """Test forgetting a memory"""
        mid = self.memory.store("Forget me")
        self.assertTrue(self.memory.forget(mid))
        self.assertIsNone(self.memory.recall(mid))

    def test_forget_nonexistent(self):
        """Test forgetting non-existent memory"""
        self.assertFalse(self.memory.forget("nonexistent"))

    def test_forget_category(self):
        """Test forgetting all memories in a category"""
        self.memory.store("A", category="temp")
        self.memory.store("B", category="temp")
        self.memory.store("C", category="keep")

        removed = self.memory.forget_category("temp")
        self.assertEqual(removed, 2)
        self.assertEqual(len(self.memory.recall_by_category("temp")), 0)
        self.assertEqual(len(self.memory.recall_by_category("keep")), 1)

    def test_eviction(self):
        """Test least-important memory eviction when over capacity"""
        # max_memories is 10, store 11
        for i in range(11):
            self.memory.store(f"Memory {i}", importance=i / 10.0)

        summary = self.memory.get_summary()
        self.assertLessEqual(summary["total_memories"], 10)

    def test_persistence(self):
        """Test memories persist across instances"""
        self.memory.store("Persistent content", category="test", memory_id="persist-001")

        # Create new instance with same storage path
        memory2 = PersistentMemory(storage_path=self.storage_path)
        recalled = memory2.recall("persist-001")
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.content, "Persistent content")

    def test_clear(self):
        """Test clearing all memories"""
        self.memory.store("A")
        self.memory.store("B")
        self.memory.clear()
        summary = self.memory.get_summary()
        self.assertEqual(summary["total_memories"], 0)

    def test_get_summary(self):
        """Test memory summary statistics"""
        self.memory.store("A", category="work", importance=0.8)
        self.memory.store("B", category="personal", importance=0.6)

        summary = self.memory.get_summary()
        self.assertEqual(summary["total_memories"], 2)
        self.assertIn("work", summary["categories"])
        self.assertIn("personal", summary["categories"])
        self.assertAlmostEqual(summary["average_importance"], 0.7, places=1)

    def test_load_corrupted_json(self):
        """Test loading from a corrupted JSON file recovers gracefully"""
        with open(self.storage_path, "w") as f:
            f.write("{invalid json!")

        memory = PersistentMemory(storage_path=self.storage_path, max_memories=10)
        self.assertEqual(len(memory.memories), 0)

    def test_load_invalid_structure(self):
        """Test loading a valid JSON file with invalid structure"""
        with open(self.storage_path, "w") as f:
            json.dump("not a dict", f)

        memory = PersistentMemory(storage_path=self.storage_path, max_memories=10)
        self.assertEqual(len(memory.memories), 0)

    def test_load_corrupted_memory_entry(self):
        """Test loading skips corrupted individual memory entries"""
        data = {
            "version": 1,
            "memory_counter": 2,
            "memories": {
                "good-001": {
                    "memory_id": "good-001",
                    "category": "test",
                    "content": "Good memory",
                },
                "bad-001": {
                    "memory_id": "bad-001",
                    # Missing required 'category' and 'content' fields
                },
            },
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f)

        memory = PersistentMemory(storage_path=self.storage_path, max_memories=10)
        self.assertEqual(len(memory.memories), 1)
        self.assertIn("good-001", memory.memories)

    def test_from_dict_missing_fields(self):
        """Test Memory.from_dict raises ValueError on missing fields"""
        with self.assertRaises(ValueError):
            Memory.from_dict({"memory_id": "test-only-id"})


if __name__ == "__main__":
    unittest.main()
