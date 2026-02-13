"""
User Profiling System

This module extends personality management with user behavior tracking,
preferences storage, and adaptive personalization based on interaction history.
"""

import logging
import json
import string
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum


class UserMoodState(Enum):
    """Detected user mood states"""
    HAPPY = "happy"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    CURIOUS = "curious"
    URGENT = "urgent"


class InteractionPattern(Enum):
    """Common interaction patterns"""
    BRIEF_RESPONSES = "brief_responses"
    DETAILED_EXPLANATIONS = "detailed_explanations"
    STEP_BY_STEP = "step_by_step"
    DIRECT_ANSWERS = "direct_answers"


@dataclass
class UserPreferences:
    """User preferences and settings"""
    user_id: str
    preferred_tone: str = "professional"
    response_length: str = "medium"  # short, medium, long
    language_style: str = "casual"  # casual, formal, technical
    interests: List[str] = field(default_factory=list)
    timezone: str = "UTC"
    notification_preferences: Dict[str, bool] = field(default_factory=dict)


@dataclass
class UserBehavior:
    """Tracked user behavior patterns"""
    user_id: str
    total_interactions: int = 0
    avg_session_duration: float = 0.0
    preferred_interaction_times: List[int] = field(default_factory=list)  # hours of day
    common_topics: Dict[str, int] = field(default_factory=dict)
    interaction_patterns: List[InteractionPattern] = field(default_factory=list)
    mood_history: List[Dict[str, Any]] = field(default_factory=list)
    last_interaction: Optional[datetime] = None


@dataclass
class UserProfile:
    """Complete user profile with preferences and behavior"""
    user_id: str
    name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    preferences: UserPreferences = field(default_factory=lambda: UserPreferences(""))
    behavior: UserBehavior = field(default_factory=lambda: UserBehavior(""))
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.preferences.user_id:
            self.preferences.user_id = self.user_id
        if not self.behavior.user_id:
            self.behavior.user_id = self.user_id


class UserProfilingSystem:
    """
    User profiling system with persistent storage and adaptive learning.
    
    Features:
    - User preference management
    - Behavior pattern tracking
    - Mood detection and adaptation
    - Persistent profile storage
    - Adaptive personalization
    """
    
    # Class constants for customization
    GREETING_WORDS = ["hi", "hello", "hey", "greetings"]
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logging.getLogger("UserProfilingSystem")
        self.logger.setLevel(logging.INFO)
        
        self.profiles: Dict[str, UserProfile] = {}
        self.storage_path = storage_path or "user_profiles.json"
        
        # Load existing profiles
        self._load_profiles()
        
        self.logger.info("UserProfilingSystem initialized")
    
    def create_profile(
        self,
        user_id: str,
        name: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """Create a new user profile"""
        if user_id in self.profiles:
            self.logger.warning(f"Profile for {user_id} already exists")
            return self.profiles[user_id]
        
        profile = UserProfile(
            user_id=user_id,
            name=name
        )
        
        # Apply custom preferences if provided
        if preferences:
            for key, value in preferences.items():
                if hasattr(profile.preferences, key):
                    setattr(profile.preferences, key, value)
        
        self.profiles[user_id] = profile
        self._save_profiles()
        
        self.logger.info(f"Created profile for user: {user_id}")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.profiles.get(user_id)
    
    def get_or_create_profile(self, user_id: str, name: Optional[str] = None) -> UserProfile:
        """Get existing profile or create new one"""
        if user_id in self.profiles:
            return self.profiles[user_id]
        return self.create_profile(user_id, name)
    
    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ):
        """Update user preferences"""
        profile = self.get_profile(user_id)
        if not profile:
            self.logger.warning(f"Profile not found: {user_id}")
            return
        
        for key, value in preferences.items():
            if hasattr(profile.preferences, key):
                setattr(profile.preferences, key, value)
        
        profile.last_updated = datetime.now()
        self._save_profiles()
        
        self.logger.debug(f"Updated preferences for {user_id}")
    
    def track_interaction(
        self,
        user_id: str,
        topic: Optional[str] = None,
        duration: Optional[float] = None,
        detected_mood: Optional[UserMoodState] = None
    ):
        """Track user interaction for behavior analysis"""
        profile = self.get_or_create_profile(user_id)
        
        # Update interaction count
        profile.behavior.total_interactions += 1
        profile.behavior.last_interaction = datetime.now()
        
        # Track topic
        if topic:
            current_count = profile.behavior.common_topics.get(topic, 0)
            profile.behavior.common_topics[topic] = current_count + 1
        
        # Update average session duration
        if duration:
            total = profile.behavior.avg_session_duration * (profile.behavior.total_interactions - 1)
            profile.behavior.avg_session_duration = (total + duration) / profile.behavior.total_interactions
        
        # Track mood
        if detected_mood:
            profile.behavior.mood_history.append({
                "timestamp": datetime.now().isoformat(),
                "mood": detected_mood.value
            })
            # Keep only last 100 mood entries
            profile.behavior.mood_history = profile.behavior.mood_history[-100:]
        
        # Track interaction time (hour of day) - keep unique hours only
        hour = datetime.now().hour
        # Convert to set for O(1) lookup, then back to list
        interaction_hours = set(profile.behavior.preferred_interaction_times)
        if hour not in interaction_hours:
            interaction_hours.add(hour)
            profile.behavior.preferred_interaction_times = sorted(list(interaction_hours))
        
        profile.last_updated = datetime.now()
        self._save_profiles()
        
        self.logger.debug(f"Tracked interaction for {user_id}")
    
    def detect_mood_from_text(self, text: str) -> UserMoodState:
        """
        Detect user mood from input text using simple heuristics.
        In production, use ML models for better accuracy.
        """
        text_lower = text.lower()
        
        # Frustration indicators
        frustration_words = ["error", "problem", "issue", "broken", "not working", "frustrated", "annoyed"]
        if any(word in text_lower for word in frustration_words):
            return UserMoodState.FRUSTRATED
        
        # Happiness indicators
        happy_words = ["great", "excellent", "perfect", "awesome", "wonderful", "thanks", "thank you"]
        if any(word in text_lower for word in happy_words):
            return UserMoodState.HAPPY
        
        # Curiosity indicators
        curiosity_words = ["how", "what", "why", "when", "where", "explain", "understand"]
        if any(word in text_lower for word in curiosity_words):
            return UserMoodState.CURIOUS
        
        # Urgency indicators
        urgency_words = ["urgent", "asap", "quickly", "immediately", "emergency", "critical"]
        if any(word in text_lower for word in urgency_words):
            return UserMoodState.URGENT
        
        return UserMoodState.NEUTRAL
    
    def adapt_response_to_user(
        self,
        user_id: str,
        response: str,
        current_mood: Optional[UserMoodState] = None
    ) -> str:
        """Adapt response based on user profile and mood"""
        profile = self.get_profile(user_id)
        if not profile:
            return response
        
        modified = response
        prefix = ""
        suffix = ""
        
        # Adapt to preferred tone first
        if profile.preferences.preferred_tone == "friendly":
            # Check for greeting words as whole words, not substrings
            words = modified.lower().split()
            has_greeting = any(word.strip(string.punctuation) in self.GREETING_WORDS for word in words)
            if not has_greeting:
                prefix = "Hey! "
        
        # Adapt to mood
        if current_mood == UserMoodState.FRUSTRATED:
            prefix = "I understand this can be frustrating. " + prefix
        elif current_mood == UserMoodState.URGENT:
            prefix = "I'll help you right away. " + prefix
        elif current_mood == UserMoodState.HAPPY:
            suffix = " 😊"
        
        # Adapt to response length preference
        if profile.preferences.response_length == "short":
            # Keep only first sentence for brevity
            sentences = modified.split(". ")
            if len(sentences) > 1:
                modified = sentences[0] + "."
        
        # Apply prefix and suffix
        modified = prefix + modified + suffix
        
        return modified
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user behavior and preferences"""
        profile = self.get_profile(user_id)
        if not profile:
            return {}
        
        # Most common topics
        sorted_topics = sorted(
            profile.behavior.common_topics.items(),
            key=lambda x: x[1],
            reverse=True
        )
        top_topics = sorted_topics[:5] if sorted_topics else []
        
        # Recent mood trend
        recent_moods = profile.behavior.mood_history[-10:] if profile.behavior.mood_history else []
        mood_distribution = {}
        for entry in recent_moods:
            mood = entry["mood"]
            mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
        
        return {
            "user_id": user_id,
            "total_interactions": profile.behavior.total_interactions,
            "avg_session_duration": profile.behavior.avg_session_duration,
            "top_topics": [{"topic": t[0], "count": t[1]} for t in top_topics],
            "preferred_interaction_times": profile.behavior.preferred_interaction_times,
            "mood_distribution": mood_distribution,
            "preferences": {
                "tone": profile.preferences.preferred_tone,
                "response_length": profile.preferences.response_length,
                "language_style": profile.preferences.language_style
            }
        }
    
    def export_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export user profile for backup or transfer"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        return {
            "user_id": profile.user_id,
            "name": profile.name,
            "created_at": profile.created_at.isoformat(),
            "last_updated": profile.last_updated.isoformat(),
            "preferences": asdict(profile.preferences),
            "behavior": {
                **asdict(profile.behavior),
                "last_interaction": profile.behavior.last_interaction.isoformat() if profile.behavior.last_interaction else None,
                "interaction_patterns": [p.value for p in profile.behavior.interaction_patterns]
            },
            "custom_data": profile.custom_data
        }
    
    def _load_profiles(self):
        """Load profiles from persistent storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                for user_id, profile_data in data.items():
                    # Reconstruct profile from JSON
                    profile = UserProfile(
                        user_id=user_id,
                        name=profile_data.get("name"),
                        created_at=datetime.fromisoformat(profile_data["created_at"]),
                        last_updated=datetime.fromisoformat(profile_data["last_updated"])
                    )
                    
                    # Load preferences
                    if "preferences" in profile_data:
                        prefs_data = profile_data["preferences"]
                        profile.preferences = UserPreferences(**prefs_data)
                    
                    # Load behavior
                    if "behavior" in profile_data:
                        beh_data = profile_data["behavior"]
                        last_int = beh_data.get("last_interaction")
                        if last_int:
                            beh_data["last_interaction"] = datetime.fromisoformat(last_int)
                        else:
                            beh_data["last_interaction"] = None
                        
                        # Convert patterns back to enum
                        patterns = beh_data.get("interaction_patterns", [])
                        beh_data["interaction_patterns"] = [
                            InteractionPattern(p) for p in patterns
                        ]
                        
                        profile.behavior = UserBehavior(**beh_data)
                    
                    profile.custom_data = profile_data.get("custom_data", {})
                    self.profiles[user_id] = profile
                
                self.logger.info(f"Loaded {len(self.profiles)} user profiles")
        except FileNotFoundError:
            self.logger.info("No existing profiles found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading profiles: {e}")
    
    def _save_profiles(self):
        """Save profiles to persistent storage"""
        try:
            data = {}
            for user_id, profile in self.profiles.items():
                data[user_id] = self.export_profile(user_id)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.debug(f"Saved {len(self.profiles)} profiles")
        except Exception as e:
            self.logger.error(f"Error saving profiles: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total_interactions = sum(p.behavior.total_interactions for p in self.profiles.values())
        
        return {
            "total_profiles": len(self.profiles),
            "total_interactions": total_interactions,
            "avg_interactions_per_user": total_interactions / len(self.profiles) if self.profiles else 0
        }
