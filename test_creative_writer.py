"""
Unit tests for Creative Writer
"""

import unittest
from creative_writer import CreativeWriter, WritingTone, ContentType


class TestCreativeWriter(unittest.TestCase):
    """Test CreativeWriter class"""
    
    def setUp(self):
        """Set up writer for tests"""
        self.writer = CreativeWriter()
    
    def test_initialization(self):
        """Test writer is initialized with templates"""
        self.assertGreater(len(self.writer.templates), 0)
    
    def test_generate_content_email(self):
        """Test generating email content"""
        content = self.writer.generate_content(
            "email-professional",
            {
                "recipient": "John",
                "purpose": "discuss project",
                "body": "Let's meet tomorrow.",
                "sender": "Alice"
            }
        )
        
        self.assertIn("John", content)
        self.assertIn("Alice", content)
        self.assertIn("discuss project", content)
    
    def test_generate_content_invalid_template(self):
        """Test generating with invalid template"""
        with self.assertRaises(ValueError):
            self.writer.generate_content("nonexistent", {})
    
    def test_generate_variations(self):
        """Test generating content variations"""
        base = "This is a test message."
        variations = self.writer.generate_variations(base, count=3)
        
        self.assertEqual(len(variations), 3)
        self.assertIn(base, variations)
    
    def test_create_ab_test(self):
        """Test creating A/B test"""
        variants = ["Version A", "Version B", "Version C"]
        test = self.writer.create_ab_test("test-001", variants)
        
        self.assertEqual(test["variant_count"], 3)
        self.assertIn("test-001", self.writer.ab_tests)
    
    def test_get_variant(self):
        """Test getting variant from A/B test"""
        variants = ["Variant 1", "Variant 2"]
        self.writer.create_ab_test("test-002", variants)
        
        variant = self.writer.get_variant("test-002", selection="random")
        self.assertIn(variant, variants)
    
    def test_record_conversion(self):
        """Test recording conversion"""
        variants = ["Variant A"]
        self.writer.create_ab_test("test-003", variants)
        
        # Get variant and record conversion
        variant = self.writer.get_variant("test-003")
        self.writer.record_conversion("test-003", variant)
        
        results = self.writer.get_ab_test_results("test-003")
        self.assertEqual(results["variants"][0]["conversions"], 1)
    
    def test_list_templates(self):
        """Test listing templates"""
        templates = self.writer.list_templates()
        self.assertGreater(len(templates), 0)
        
        # Filter by type
        email_templates = self.writer.list_templates(ContentType.EMAIL)
        self.assertTrue(all(t["content_type"] == "email" for t in email_templates))
    
    def test_enhance_clarity(self):
        """Test clarity enhancement"""
        text = "hello   world.  this is  a test."
        enhanced = self.writer.enhance_clarity(text)
        
        self.assertNotIn("  ", enhanced)  # No double spaces
        self.assertTrue(enhanced[0].isupper())  # Capitalized


if __name__ == "__main__":
    unittest.main()
