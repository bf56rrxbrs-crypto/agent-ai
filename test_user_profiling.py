"""
Tests for User Profiling System
"""

import unittest
import os
import tempfile
from datetime import datetime

from user_profiling import (
    UserProfilingSystem,
    UserProfile,
    UserPreferences,
    UserMoodState,
    InteractionPattern
)


class TestUserProfilingSystem(unittest.TestCase):
    """Test UserProfilingSystem class"""
    
    def setUp(self):
        """Set up test system with temporary storage"""
        # Use temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.system = UserProfilingSystem(storage_path=self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_create_profile(self):
        """Test creating a user profile"""
        profile = self.system.create_profile("user-123", name="Test User")
        
        self.assertEqual(profile.user_id, "user-123")
        self.assertEqual(profile.name, "Test User")
        self.assertIsNotNone(profile.created_at)
        self.assertEqual(profile.behavior.total_interactions, 0)
    
    def test_get_or_create_profile(self):
        """Test getting or creating profile"""
        profile1 = self.system.get_or_create_profile("user-456", name="User 456")
        profile2 = self.system.get_or_create_profile("user-456")
        
        self.assertEqual(profile1.user_id, profile2.user_id)
        self.assertEqual(len(self.system.profiles), 1)
    
    def test_update_preferences(self):
        """Test updating user preferences"""
        self.system.create_profile("user-789")
        
        self.system.update_preferences("user-789", {
            "preferred_tone": "friendly",
            "response_length": "short"
        })
        
        profile = self.system.get_profile("user-789")
        self.assertEqual(profile.preferences.preferred_tone, "friendly")
        self.assertEqual(profile.preferences.response_length, "short")
    
    def test_track_interaction(self):
        """Test tracking user interactions"""
        self.system.create_profile("user-001")
        
        self.system.track_interaction(
            "user-001",
            topic="weather",
            duration=2.5,
            detected_mood=UserMoodState.HAPPY
        )
        
        profile = self.system.get_profile("user-001")
        self.assertEqual(profile.behavior.total_interactions, 1)
        self.assertIn("weather", profile.behavior.common_topics)
        self.assertEqual(profile.behavior.avg_session_duration, 2.5)
        self.assertEqual(len(profile.behavior.mood_history), 1)
    
    def test_mood_detection(self):
        """Test mood detection from text"""
        frustrated = self.system.detect_mood_from_text("This is broken and not working!")
        self.assertEqual(frustrated, UserMoodState.FRUSTRATED)
        
        happy = self.system.detect_mood_from_text("Thank you so much, this is perfect!")
        self.assertEqual(happy, UserMoodState.HAPPY)
        
        curious = self.system.detect_mood_from_text("How does this work?")
        self.assertEqual(curious, UserMoodState.CURIOUS)
        
        urgent = self.system.detect_mood_from_text("I need this fixed immediately!")
        self.assertEqual(urgent, UserMoodState.URGENT)
    
    def test_adapt_response_to_user(self):
        """Test adapting responses to user profile"""
        profile = self.system.create_profile("user-002")
        profile.preferences.preferred_tone = "friendly"
        profile.preferences.response_length = "short"
        
        response = "This is a long explanation about how things work."
        adapted = self.system.adapt_response_to_user("user-002", response)
        
        # Should add friendly greeting
        self.assertIn("Hey", adapted)
    
    def test_adapt_response_to_mood(self):
        """Test adapting responses based on mood"""
        self.system.create_profile("user-003")
        
        frustrated_response = self.system.adapt_response_to_user(
            "user-003",
            "Here is the solution.",
            current_mood=UserMoodState.FRUSTRATED
        )
        
        self.assertIn("frustrating", frustrated_response.lower())
    
    def test_get_user_insights(self):
        """Test getting user insights"""
        self.system.create_profile("user-004")
        
        # Track some interactions
        for i in range(5):
            self.system.track_interaction(
                "user-004",
                topic="programming",
                duration=3.0,
                detected_mood=UserMoodState.HAPPY
            )
        
        insights = self.system.get_user_insights("user-004")
        
        self.assertEqual(insights["total_interactions"], 5)
        self.assertIn("programming", [t["topic"] for t in insights["top_topics"]])
        self.assertIn("happy", insights["mood_distribution"])
    
    def test_export_profile(self):
        """Test exporting user profile"""
        profile = self.system.create_profile("user-005", name="Export User")
        self.system.track_interaction("user-005", topic="test")
        
        exported = self.system.export_profile("user-005")
        
        self.assertEqual(exported["user_id"], "user-005")
        self.assertEqual(exported["name"], "Export User")
        self.assertIn("preferences", exported)
        self.assertIn("behavior", exported)
    
    def test_persistence(self):
        """Test profile persistence across sessions"""
        # Create and save profiles
        self.system.create_profile("user-persist-1", name="Persist User 1")
        self.system.create_profile("user-persist-2", name="Persist User 2")
        self.system.track_interaction("user-persist-1", topic="testing")
        
        # Create new system instance with same storage
        new_system = UserProfilingSystem(storage_path=self.temp_file.name)
        
        # Verify profiles were loaded
        self.assertEqual(len(new_system.profiles), 2)
        profile = new_system.get_profile("user-persist-1")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "Persist User 1")
        self.assertEqual(profile.behavior.total_interactions, 1)
    
    def test_get_stats(self):
        """Test getting system statistics"""
        self.system.create_profile("user-stats-1")
        self.system.create_profile("user-stats-2")
        self.system.track_interaction("user-stats-1", topic="test")
        self.system.track_interaction("user-stats-2", topic="test")
        
        stats = self.system.get_stats()
        
        self.assertEqual(stats["total_profiles"], 2)
        self.assertEqual(stats["total_interactions"], 2)
        self.assertEqual(stats["avg_interactions_per_user"], 1.0)


if __name__ == "__main__":
    unittest.main()
