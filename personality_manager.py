"""
Personality and Behavior Customization Module

This module allows users to define their AI agent's personality traits
and adjusts responses based on user interactions over time.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class PersonalityTrait(Enum):
    """Predefined personality traits"""
    EMPATHETIC = "empathetic"
    HUMOROUS = "humorous"
    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


class PersonalityProfile:
    """Represents a personality profile with multiple traits"""
    
    def __init__(self, profile_id: str, name: str, traits: Dict[PersonalityTrait, float]):
        """
        Initialize a personality profile.
        
        Args:
            profile_id: Unique identifier for the profile
            name: Human-readable name
            traits: Dictionary mapping traits to intensity (0.0-1.0)
        """
        self.profile_id = profile_id
        self.name = name
        self.traits = traits
        self.interaction_count = 0
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def get_trait_intensity(self, trait: PersonalityTrait) -> float:
        """Get the intensity of a specific trait (0.0-1.0)"""
        return self.traits.get(trait, 0.0)
    
    def update_trait(self, trait: PersonalityTrait, intensity: float):
        """Update the intensity of a trait based on interactions"""
        if 0.0 <= intensity <= 1.0:
            self.traits[trait] = intensity
            self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "traits": {trait.value: intensity for trait, intensity in self.traits.items()},
            "interaction_count": self.interaction_count,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


class PersonalityManager:
    """
    Manages personality profiles and adjusts agent behavior based on personality traits.
    
    Features:
    - Multiple personality profiles
    - Dynamic trait adjustment based on user interactions
    - Personality-based response modification
    - Learning from user feedback
    """
    
    def __init__(self):
        self.profiles: Dict[str, PersonalityProfile] = {}
        self.active_profile_id: Optional[str] = None
        self.interaction_history: List[Dict[str, Any]] = []
        
        # Setup logging
        self.logger = logging.getLogger("PersonalityManager")
        self.logger.setLevel(logging.INFO)
        
        # Create default profiles
        self._create_default_profiles()
        
        self.logger.info("PersonalityManager initialized")
    
    def _create_default_profiles(self):
        """Create default personality profiles"""
        
        # Empathetic profile
        empathetic = PersonalityProfile(
            "empathetic-001",
            "Empathetic Assistant",
            {
                PersonalityTrait.EMPATHETIC: 0.9,
                PersonalityTrait.FORMAL: 0.3,
                PersonalityTrait.CASUAL: 0.6
            }
        )
        self.profiles[empathetic.profile_id] = empathetic
        
        # Humorous profile
        humorous = PersonalityProfile(
            "humorous-001",
            "Humorous Assistant",
            {
                PersonalityTrait.HUMOROUS: 0.9,
                PersonalityTrait.CASUAL: 0.8,
                PersonalityTrait.CREATIVE: 0.7
            }
        )
        self.profiles[humorous.profile_id] = humorous
        
        # Formal profile
        formal = PersonalityProfile(
            "formal-001",
            "Formal Assistant",
            {
                PersonalityTrait.FORMAL: 0.9,
                PersonalityTrait.PROFESSIONAL: 0.9,
                PersonalityTrait.ANALYTICAL: 0.7
            }
        )
        self.profiles[formal.profile_id] = formal
        
        # Professional profile
        professional = PersonalityProfile(
            "professional-001",
            "Professional Assistant",
            {
                PersonalityTrait.PROFESSIONAL: 0.9,
                PersonalityTrait.FORMAL: 0.7,
                PersonalityTrait.ANALYTICAL: 0.8
            }
        )
        self.profiles[professional.profile_id] = professional
        
        # Set default active profile
        self.active_profile_id = "professional-001"
    
    def create_profile(self, profile_id: str, name: str, traits: Dict[PersonalityTrait, float]) -> PersonalityProfile:
        """Create a custom personality profile"""
        profile = PersonalityProfile(profile_id, name, traits)
        self.profiles[profile_id] = profile
        self.logger.info(f"Created personality profile: {name}")
        return profile
    
    def set_active_profile(self, profile_id: str):
        """Set the active personality profile"""
        if profile_id in self.profiles:
            self.active_profile_id = profile_id
            self.logger.info(f"Active profile set to: {self.profiles[profile_id].name}")
        else:
            raise ValueError(f"Profile {profile_id} not found")
    
    def get_active_profile(self) -> Optional[PersonalityProfile]:
        """Get the currently active personality profile"""
        if self.active_profile_id:
            return self.profiles.get(self.active_profile_id)
        return None
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all available personality profiles"""
        return [
            {
                "profile_id": profile.profile_id,
                "name": profile.name,
                "is_active": profile.profile_id == self.active_profile_id
            }
            for profile in self.profiles.values()
        ]
    
    def adjust_response(self, original_response: str) -> str:
        """
        Adjust a response based on the active personality profile.
        
        This is a placeholder implementation that adds personality-specific
        modifications to responses.
        """
        profile = self.get_active_profile()
        if not profile:
            return original_response
        
        modified_response = original_response
        
        # Apply personality modifications based on dominant traits
        if profile.get_trait_intensity(PersonalityTrait.EMPATHETIC) > 0.7:
            # Add empathetic language
            if not any(word in modified_response.lower() for word in ["understand", "appreciate", "feel"]):
                modified_response = f"I understand. {modified_response}"
        
        if profile.get_trait_intensity(PersonalityTrait.HUMOROUS) > 0.7:
            # Add a touch of humor (subtle)
            modified_response = modified_response.replace(".", " 😊")
        
        if profile.get_trait_intensity(PersonalityTrait.FORMAL) > 0.7:
            # Make more formal
            modified_response = modified_response.replace("I'm", "I am")
            modified_response = modified_response.replace("don't", "do not")
            modified_response = modified_response.replace("won't", "will not")
        
        return modified_response
    
    def record_interaction(self, user_input: str, agent_response: str, feedback: Optional[str] = None):
        """
        Record an interaction for learning and adaptation.
        
        This enables the system to learn from user interactions over time.
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "profile_id": self.active_profile_id,
            "user_input": user_input,
            "agent_response": agent_response,
            "feedback": feedback
        }
        
        self.interaction_history.append(interaction)
        
        # Update interaction count for active profile
        profile = self.get_active_profile()
        if profile:
            profile.interaction_count += 1
            
            # Simple learning: adjust traits based on feedback
            if feedback == "positive":
                # Reinforce current traits slightly
                for trait in profile.traits:
                    current = profile.traits[trait]
                    profile.traits[trait] = min(1.0, current + 0.01)
            elif feedback == "negative":
                # Slightly reduce trait intensities
                for trait in profile.traits:
                    current = profile.traits[trait]
                    profile.traits[trait] = max(0.0, current - 0.01)
        
        self.logger.debug(f"Recorded interaction with feedback: {feedback}")
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get statistics about interactions"""
        profile = self.get_active_profile()
        
        return {
            "total_interactions": len(self.interaction_history),
            "active_profile": profile.name if profile else None,
            "profile_interactions": profile.interaction_count if profile else 0,
            "recent_interactions": len([
                i for i in self.interaction_history[-100:]
                if i["profile_id"] == self.active_profile_id
            ])
        }
    
    def export_profile(self, profile_id: str) -> Dict[str, Any]:
        """Export a profile configuration"""
        if profile_id in self.profiles:
            return self.profiles[profile_id].to_dict()
        raise ValueError(f"Profile {profile_id} not found")
    
    def import_profile(self, profile_data: Dict[str, Any]) -> PersonalityProfile:
        """Import a profile from configuration data"""
        traits = {
            PersonalityTrait(trait_name): intensity
            for trait_name, intensity in profile_data["traits"].items()
        }
        
        profile = PersonalityProfile(
            profile_data["profile_id"],
            profile_data["name"],
            traits
        )
        
        self.profiles[profile.profile_id] = profile
        self.logger.info(f"Imported profile: {profile.name}")
        return profile
