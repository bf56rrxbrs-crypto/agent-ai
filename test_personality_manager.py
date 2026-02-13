"""
Unit tests for Personality Manager
"""

import unittest
from personality_manager import PersonalityManager, PersonalityTrait, PersonalityProfile


class TestPersonalityProfile(unittest.TestCase):
    """Test PersonalityProfile class"""
    
    def test_profile_initialization(self):
        """Test profile is initialized correctly"""
        traits = {
            PersonalityTrait.EMPATHETIC: 0.8,
            PersonalityTrait.FORMAL: 0.5
        }
        profile = PersonalityProfile("test-001", "Test Profile", traits)
        
        self.assertEqual(profile.profile_id, "test-001")
        self.assertEqual(profile.name, "Test Profile")
        self.assertEqual(profile.get_trait_intensity(PersonalityTrait.EMPATHETIC), 0.8)
        self.assertEqual(profile.interaction_count, 0)
    
    def test_get_trait_intensity(self):
        """Test getting trait intensity"""
        traits = {PersonalityTrait.HUMOROUS: 0.9}
        profile = PersonalityProfile("test-002", "Test", traits)
        
        self.assertEqual(profile.get_trait_intensity(PersonalityTrait.HUMOROUS), 0.9)
        self.assertEqual(profile.get_trait_intensity(PersonalityTrait.FORMAL), 0.0)
    
    def test_update_trait(self):
        """Test updating trait intensity"""
        traits = {PersonalityTrait.FORMAL: 0.5}
        profile = PersonalityProfile("test-003", "Test", traits)
        
        profile.update_trait(PersonalityTrait.FORMAL, 0.7)
        self.assertEqual(profile.get_trait_intensity(PersonalityTrait.FORMAL), 0.7)
        
        # Test boundary validation
        profile.update_trait(PersonalityTrait.FORMAL, 1.5)  # Invalid, should not update
        self.assertEqual(profile.get_trait_intensity(PersonalityTrait.FORMAL), 0.7)
    
    def test_to_dict(self):
        """Test converting profile to dictionary"""
        traits = {PersonalityTrait.PROFESSIONAL: 0.8}
        profile = PersonalityProfile("test-004", "Test", traits)
        
        profile_dict = profile.to_dict()
        self.assertEqual(profile_dict["profile_id"], "test-004")
        self.assertEqual(profile_dict["name"], "Test")
        self.assertIn("professional", profile_dict["traits"])


class TestPersonalityManager(unittest.TestCase):
    """Test PersonalityManager class"""
    
    def setUp(self):
        """Set up test manager"""
        self.manager = PersonalityManager()
    
    def test_initialization(self):
        """Test manager is initialized with default profiles"""
        self.assertGreater(len(self.manager.profiles), 0)
        self.assertIsNotNone(self.manager.active_profile_id)
        
        # Check default profiles exist
        profile_ids = [p.profile_id for p in self.manager.profiles.values()]
        self.assertIn("empathetic-001", profile_ids)
        self.assertIn("humorous-001", profile_ids)
        self.assertIn("formal-001", profile_ids)
    
    def test_create_profile(self):
        """Test creating a custom profile"""
        traits = {
            PersonalityTrait.CREATIVE: 0.9,
            PersonalityTrait.CASUAL: 0.7
        }
        profile = self.manager.create_profile("custom-001", "Custom Profile", traits)
        
        self.assertEqual(profile.profile_id, "custom-001")
        self.assertIn("custom-001", self.manager.profiles)
    
    def test_set_active_profile(self):
        """Test setting active profile"""
        self.manager.set_active_profile("empathetic-001")
        self.assertEqual(self.manager.active_profile_id, "empathetic-001")
        
        # Test invalid profile
        with self.assertRaises(ValueError):
            self.manager.set_active_profile("nonexistent")
    
    def test_get_active_profile(self):
        """Test getting active profile"""
        self.manager.set_active_profile("humorous-001")
        profile = self.manager.get_active_profile()
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profile_id, "humorous-001")
    
    def test_list_profiles(self):
        """Test listing all profiles"""
        profiles = self.manager.list_profiles()
        
        self.assertGreater(len(profiles), 0)
        self.assertTrue(all("profile_id" in p for p in profiles))
        self.assertTrue(all("name" in p for p in profiles))
        self.assertTrue(any(p["is_active"] for p in profiles))
    
    def test_adjust_response_empathetic(self):
        """Test response adjustment for empathetic profile"""
        self.manager.set_active_profile("empathetic-001")
        
        original = "Here is your answer."
        adjusted = self.manager.adjust_response(original)
        
        self.assertIn("understand", adjusted.lower())
    
    def test_adjust_response_formal(self):
        """Test response adjustment for formal profile"""
        self.manager.set_active_profile("formal-001")
        
        original = "I'm ready to help, don't worry."
        adjusted = self.manager.adjust_response(original)
        
        self.assertNotIn("I'm", adjusted)
        self.assertNotIn("don't", adjusted)
        self.assertIn("I am", adjusted)
        self.assertIn("do not", adjusted)
    
    def test_record_interaction(self):
        """Test recording interactions"""
        initial_count = len(self.manager.interaction_history)
        
        self.manager.record_interaction(
            "What is the weather?",
            "The weather is sunny.",
            "positive"
        )
        
        self.assertEqual(len(self.manager.interaction_history), initial_count + 1)
        
        profile = self.manager.get_active_profile()
        self.assertEqual(profile.interaction_count, 1)
    
    def test_record_interaction_with_feedback(self):
        """Test interaction recording adjusts traits based on feedback"""
        self.manager.set_active_profile("empathetic-001")
        profile = self.manager.get_active_profile()
        
        # Get initial trait values
        initial_traits = {trait: profile.get_trait_intensity(trait) for trait in profile.traits}
        
        # Record positive feedback
        for _ in range(5):
            self.manager.record_interaction("test", "response", "positive")
        
        # Check traits increased
        for trait in profile.traits:
            current = profile.get_trait_intensity(trait)
            self.assertGreaterEqual(current, initial_traits[trait])
    
    def test_get_interaction_stats(self):
        """Test getting interaction statistics"""
        self.manager.record_interaction("test1", "response1")
        self.manager.record_interaction("test2", "response2")
        
        stats = self.manager.get_interaction_stats()
        
        self.assertIn("total_interactions", stats)
        self.assertIn("active_profile", stats)
        self.assertGreaterEqual(stats["total_interactions"], 2)
    
    def test_export_import_profile(self):
        """Test exporting and importing profiles"""
        # Export a profile
        profile_data = self.manager.export_profile("empathetic-001")
        
        self.assertIn("profile_id", profile_data)
        self.assertIn("traits", profile_data)
        
        # Modify and import
        profile_data["profile_id"] = "imported-001"
        profile_data["name"] = "Imported Profile"
        
        imported = self.manager.import_profile(profile_data)
        
        self.assertEqual(imported.profile_id, "imported-001")
        self.assertIn("imported-001", self.manager.profiles)


if __name__ == "__main__":
    unittest.main()
