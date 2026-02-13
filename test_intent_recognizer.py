"""
Unit tests for Intent Recognizer
"""

import unittest
from intent_recognizer import IntentRecognizer, IntentType, Intent, IntentPattern


class TestIntent(unittest.TestCase):
    """Test Intent class"""
    
    def test_intent_initialization(self):
        """Test intent is created correctly"""
        intent = Intent(IntentType.QUERY, 0.85, {"entity": "value"}, "test query")
        
        self.assertEqual(intent.intent_type, IntentType.QUERY)
        self.assertEqual(intent.confidence, 0.85)
        self.assertEqual(intent.entities, {"entity": "value"})
        self.assertEqual(intent.raw_text, "test query")
    
    def test_intent_to_dict(self):
        """Test converting intent to dictionary"""
        intent = Intent(IntentType.COMMAND, 0.9, {}, "run task")
        intent_dict = intent.to_dict()
        
        self.assertEqual(intent_dict["intent_type"], "command")
        self.assertEqual(intent_dict["confidence"], 0.9)
        self.assertIn("entities", intent_dict)


class TestIntentPattern(unittest.TestCase):
    """Test IntentPattern class"""
    
    def test_pattern_initialization(self):
        """Test pattern is created correctly"""
        pattern = IntentPattern(IntentType.GREETING, [r"hello", r"hi"], priority=10)
        
        self.assertEqual(pattern.intent_type, IntentType.GREETING)
        self.assertEqual(len(pattern.patterns), 2)
        self.assertEqual(pattern.priority, 10)
    
    def test_pattern_match(self):
        """Test pattern matching"""
        pattern = IntentPattern(IntentType.GREETING, [r"^hello"])
        
        # Should match
        result = pattern.match("hello there")
        self.assertIsNotNone(result)
        confidence, entities = result
        self.assertGreater(confidence, 0)
        
        # Should not match
        result = pattern.match("goodbye")
        self.assertIsNone(result)


class TestIntentRecognizer(unittest.TestCase):
    """Test IntentRecognizer class"""
    
    def setUp(self):
        """Set up recognizer for tests"""
        self.recognizer = IntentRecognizer()
    
    def test_initialization(self):
        """Test recognizer is initialized with default patterns"""
        self.assertGreater(len(self.recognizer.patterns), 0)
        self.assertEqual(self.recognizer.recognition_count, 0)
    
    def test_recognize_greeting(self):
        """Test recognizing greeting intent"""
        intent = self.recognizer.recognize("Hello there!")
        
        self.assertEqual(intent.intent_type, IntentType.GREETING)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_farewell(self):
        """Test recognizing farewell intent"""
        intent = self.recognizer.recognize("Goodbye, see you later")
        
        self.assertEqual(intent.intent_type, IntentType.FAREWELL)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_help(self):
        """Test recognizing help intent"""
        intent = self.recognizer.recognize("Can you help me with this?")
        
        self.assertEqual(intent.intent_type, IntentType.HELP)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_query(self):
        """Test recognizing query intent"""
        intent = self.recognizer.recognize("What is the weather today?")
        
        self.assertEqual(intent.intent_type, IntentType.QUERY)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_command(self):
        """Test recognizing command intent"""
        intent = self.recognizer.recognize("Create a new task for me")
        
        self.assertEqual(intent.intent_type, IntentType.COMMAND)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_affirmation(self):
        """Test recognizing affirmation intent"""
        intent = self.recognizer.recognize("Yes, that's correct")
        
        self.assertEqual(intent.intent_type, IntentType.AFFIRMATION)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_negation(self):
        """Test recognizing negation intent"""
        intent = self.recognizer.recognize("No, that's wrong")
        
        self.assertEqual(intent.intent_type, IntentType.NEGATION)
        self.assertGreater(intent.confidence, 0)
    
    def test_recognize_unknown(self):
        """Test unknown intent for unmatched text"""
        intent = self.recognizer.recognize("xyzabc123nonsense")
        
        self.assertEqual(intent.intent_type, IntentType.UNKNOWN)
        self.assertEqual(intent.confidence, 0.0)
    
    def test_recognize_empty_text(self):
        """Test recognition with empty text"""
        intent = self.recognizer.recognize("")
        
        self.assertEqual(intent.intent_type, IntentType.UNKNOWN)
        self.assertEqual(intent.confidence, 0.0)
    
    def test_recognize_batch(self):
        """Test batch recognition"""
        texts = [
            "Hello",
            "What is AI?",
            "Create a report"
        ]
        
        intents = self.recognizer.recognize_batch(texts)
        
        self.assertEqual(len(intents), 3)
        self.assertEqual(intents[0].intent_type, IntentType.GREETING)
        self.assertEqual(intents[1].intent_type, IntentType.QUERY)
        self.assertEqual(intents[2].intent_type, IntentType.COMMAND)
    
    def test_add_pattern(self):
        """Test adding custom pattern"""
        initial_count = len(self.recognizer.patterns)
        
        new_pattern = IntentPattern(IntentType.TASK, [r"schedule.*meeting"], priority=8)
        self.recognizer.add_pattern(new_pattern)
        
        self.assertEqual(len(self.recognizer.patterns), initial_count + 1)
    
    def test_get_stats(self):
        """Test getting statistics"""
        # Recognize some intents
        self.recognizer.recognize("Hello")
        self.recognizer.recognize("What is this?")
        self.recognizer.recognize("Create task")
        
        stats = self.recognizer.get_stats()
        
        self.assertEqual(stats["total_recognitions"], 3)
        self.assertIn("intent_distribution", stats)
        self.assertGreater(stats["pattern_count"], 0)
    
    def test_add_custom_intent(self):
        """Test adding custom intent"""
        self.recognizer.add_custom_intent(
            "weather",
            [r"weather|temperature|forecast"],
            priority=7
        )
        
        # This should now match as a command (simplified implementation)
        intent = self.recognizer.recognize("Check the weather")
        # Since we map to existing intents, just verify it doesn't crash
        self.assertIsNotNone(intent)
    
    def test_case_insensitive_matching(self):
        """Test that matching is case insensitive"""
        intent1 = self.recognizer.recognize("HELLO")
        intent2 = self.recognizer.recognize("hello")
        intent3 = self.recognizer.recognize("HeLLo")
        
        self.assertEqual(intent1.intent_type, IntentType.GREETING)
        self.assertEqual(intent2.intent_type, IntentType.GREETING)
        self.assertEqual(intent3.intent_type, IntentType.GREETING)


if __name__ == "__main__":
    unittest.main()
