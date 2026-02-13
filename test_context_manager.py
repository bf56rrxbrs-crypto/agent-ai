"""
Unit tests for Context Manager
"""

import unittest
from datetime import datetime, timedelta
from context_manager import ContextManager, ConversationContext


class TestConversationContext(unittest.TestCase):
    """Test ConversationContext class"""
    
    def test_context_initialization(self):
        """Test context is initialized correctly"""
        context = ConversationContext(
            context_id="ctx-001",
            user_id="user-123",
            session_id="session-456"
        )
        
        self.assertEqual(context.context_id, "ctx-001")
        self.assertEqual(context.user_id, "user-123")
        self.assertEqual(context.session_id, "session-456")
        self.assertEqual(context.turn_count, 0)
        self.assertEqual(len(context.history), 0)
    
    def test_add_turn(self):
        """Test adding conversation turn"""
        context = ConversationContext("ctx-001")
        
        context.add_turn("Hello", "Hi there!", "greeting")
        
        self.assertEqual(context.turn_count, 1)
        self.assertEqual(len(context.history), 1)
        self.assertEqual(context.last_intent, "greeting")
        
        turn = context.history[0]
        self.assertEqual(turn["user_input"], "Hello")
        self.assertEqual(turn["agent_response"], "Hi there!")
    
    def test_add_entity(self):
        """Test adding entities"""
        context = ConversationContext("ctx-001")
        
        context.add_entity("user_name", "John")
        context.add_entity("location", "New York")
        
        self.assertEqual(context.entities["user_name"], "John")
        self.assertEqual(context.entities["location"], "New York")
    
    def test_add_topic(self):
        """Test adding topics"""
        context = ConversationContext("ctx-001")
        
        context.add_topic("weather")
        context.add_topic("sports")
        context.add_topic("weather")  # Duplicate
        
        self.assertEqual(len(context.topics), 2)
        self.assertIn("weather", context.topics)
        self.assertIn("sports", context.topics)
    
    def test_get_recent_history(self):
        """Test getting recent history"""
        context = ConversationContext("ctx-001")
        
        for i in range(10):
            context.add_turn(f"Input {i}", f"Response {i}")
        
        recent = context.get_recent_history(3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[-1]["user_input"], "Input 9")
    
    def test_clear_history(self):
        """Test clearing history"""
        context = ConversationContext("ctx-001")
        
        context.add_turn("Hello", "Hi")
        context.add_entity("name", "John")
        
        context.clear_history()
        
        self.assertEqual(len(context.history), 0)
        self.assertEqual(context.turn_count, 0)
        # Entities should be preserved
        self.assertEqual(context.entities["name"], "John")
    
    def test_to_dict(self):
        """Test converting context to dictionary"""
        context = ConversationContext("ctx-001", user_id="user-123")
        context.add_turn("Hello", "Hi")
        
        context_dict = context.to_dict()
        
        self.assertEqual(context_dict["context_id"], "ctx-001")
        self.assertEqual(context_dict["user_id"], "user-123")
        self.assertEqual(context_dict["turn_count"], 1)
        self.assertEqual(context_dict["history_length"], 1)


class TestContextManager(unittest.TestCase):
    """Test ContextManager class"""
    
    def setUp(self):
        """Set up manager for tests"""
        self.manager = ContextManager(default_ttl=3600)
    
    def test_initialization(self):
        """Test manager is initialized correctly"""
        self.assertEqual(len(self.manager.contexts), 0)
        self.assertEqual(self.manager.default_ttl, 3600)
    
    def test_create_context(self):
        """Test creating a context"""
        context = self.manager.create_context(
            "ctx-001",
            user_id="user-123",
            session_id="session-456"
        )
        
        self.assertIsNotNone(context)
        self.assertEqual(context.context_id, "ctx-001")
        self.assertIn("ctx-001", self.manager.contexts)
    
    def test_get_context(self):
        """Test getting a context"""
        self.manager.create_context("ctx-001")
        
        context = self.manager.get_context("ctx-001")
        
        self.assertIsNotNone(context)
        self.assertEqual(context.context_id, "ctx-001")
    
    def test_get_nonexistent_context(self):
        """Test getting non-existent context"""
        context = self.manager.get_context("nonexistent")
        
        self.assertIsNone(context)
    
    def test_get_or_create_context(self):
        """Test get or create context"""
        # First call should create
        context1 = self.manager.get_or_create_context("ctx-001")
        self.assertIsNotNone(context1)
        
        # Second call should get existing
        context2 = self.manager.get_or_create_context("ctx-001")
        self.assertEqual(context1.context_id, context2.context_id)
    
    def test_delete_context(self):
        """Test deleting a context"""
        self.manager.create_context("ctx-001")
        
        result = self.manager.delete_context("ctx-001")
        
        self.assertTrue(result)
        self.assertNotIn("ctx-001", self.manager.contexts)
        
        # Try deleting non-existent
        result = self.manager.delete_context("nonexistent")
        self.assertFalse(result)
    
    def test_update_context(self):
        """Test updating context"""
        self.manager.create_context("ctx-001")
        
        self.manager.update_context(
            "ctx-001",
            "What's the weather?",
            "It's sunny today",
            intent="query",
            entities={"topic": "weather"},
            topics=["weather", "climate"]
        )
        
        context = self.manager.get_context("ctx-001")
        
        self.assertEqual(context.turn_count, 1)
        self.assertEqual(context.last_intent, "query")
        self.assertEqual(context.entities["topic"], "weather")
        self.assertIn("weather", context.topics)
    
    def test_update_nonexistent_context(self):
        """Test updating non-existent context creates it"""
        self.manager.update_context(
            "ctx-new",
            "Hello",
            "Hi there"
        )
        
        context = self.manager.get_context("ctx-new")
        self.assertIsNotNone(context)
        self.assertEqual(context.turn_count, 1)
    
    def test_get_context_summary(self):
        """Test getting context summary"""
        self.manager.create_context("ctx-001")
        self.manager.update_context("ctx-001", "Hello", "Hi")
        self.manager.update_context("ctx-001", "How are you?", "I'm good")
        
        summary = self.manager.get_context_summary("ctx-001")
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary["context_id"], "ctx-001")
        self.assertEqual(summary["turn_count"], 2)
        self.assertIn("recent_turns", summary)
    
    def test_get_summary_nonexistent(self):
        """Test getting summary for non-existent context"""
        summary = self.manager.get_context_summary("nonexistent")
        self.assertIsNone(summary)
    
    def test_list_contexts(self):
        """Test listing contexts"""
        self.manager.create_context("ctx-001", user_id="user-1")
        self.manager.create_context("ctx-002", user_id="user-2")
        self.manager.create_context("ctx-003", user_id="user-1")
        
        # List all
        all_contexts = self.manager.list_contexts()
        self.assertEqual(len(all_contexts), 3)
        
        # Filter by user
        user1_contexts = self.manager.list_contexts(user_id="user-1")
        self.assertEqual(len(user1_contexts), 2)
    
    def test_cleanup_expired(self):
        """Test cleaning up expired contexts"""
        # Create contexts with different ages
        manager = ContextManager(default_ttl=1)  # 1 second TTL
        
        manager.create_context("ctx-001")
        manager.create_context("ctx-002")
        
        # Make one context old
        manager.contexts["ctx-001"].last_updated = datetime.now() - timedelta(seconds=2)
        
        expired_count = manager.cleanup_expired()
        
        self.assertEqual(expired_count, 1)
        self.assertNotIn("ctx-001", manager.contexts)
        self.assertIn("ctx-002", manager.contexts)
    
    def test_get_stats(self):
        """Test getting statistics"""
        self.manager.create_context("ctx-001")
        self.manager.update_context("ctx-001", "Hello", "Hi")
        self.manager.update_context("ctx-001", "How are you?", "Good")
        
        self.manager.create_context("ctx-002")
        self.manager.update_context("ctx-002", "Test", "Response")
        
        stats = self.manager.get_stats()
        
        self.assertEqual(stats["active_contexts"], 2)
        self.assertEqual(stats["total_turns"], 3)
        self.assertGreater(stats["average_turns_per_context"], 0)
    
    def test_merge_contexts(self):
        """Test merging contexts"""
        # Create source context
        self.manager.create_context("ctx-source")
        self.manager.update_context("ctx-source", "Hello", "Hi")
        source = self.manager.get_context("ctx-source")
        source.add_entity("name", "John")
        source.add_topic("greetings")
        
        # Create target context
        self.manager.create_context("ctx-target")
        self.manager.update_context("ctx-target", "Goodbye", "Bye")
        target = self.manager.get_context("ctx-target")
        target.add_entity("location", "NYC")
        
        # Merge
        result = self.manager.merge_contexts("ctx-source", "ctx-target")
        
        self.assertTrue(result)
        self.assertNotIn("ctx-source", self.manager.contexts)
        
        merged = self.manager.get_context("ctx-target")
        self.assertEqual(merged.turn_count, 2)
        self.assertEqual(merged.entities["name"], "John")
        self.assertEqual(merged.entities["location"], "NYC")
        self.assertIn("greetings", merged.topics)
    
    def test_merge_nonexistent_contexts(self):
        """Test merging with non-existent contexts"""
        self.manager.create_context("ctx-001")
        
        # Try to merge with non-existent source
        result = self.manager.merge_contexts("nonexistent", "ctx-001")
        self.assertFalse(result)
        
        # Try to merge with non-existent target
        result = self.manager.merge_contexts("ctx-001", "nonexistent")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
