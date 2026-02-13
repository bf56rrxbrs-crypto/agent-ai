"""
Intent Recognition Module

This module provides natural language understanding capabilities to detect
user intents from commands and queries.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass


class IntentType(Enum):
    """Common intent types"""
    QUERY = "query"  # Information request
    COMMAND = "command"  # Action request
    GREETING = "greeting"  # Greetings
    FAREWELL = "farewell"  # Goodbyes
    AFFIRMATION = "affirmation"  # Yes/agree
    NEGATION = "negation"  # No/disagree
    HELP = "help"  # Help request
    FEEDBACK = "feedback"  # User feedback
    TASK = "task"  # Task creation/management
    UNKNOWN = "unknown"  # Unknown intent


@dataclass
class Intent:
    """Represents a recognized intent"""
    intent_type: IntentType
    confidence: float  # 0.0-1.0
    entities: Dict[str, Any]  # Extracted entities
    raw_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "entities": self.entities,
            "raw_text": self.raw_text
        }


class IntentPattern:
    """Pattern matching for intent recognition"""
    
    def __init__(self, intent_type: IntentType, patterns: List[str], priority: int = 1):
        """
        Initialize intent pattern.
        
        Args:
            intent_type: The intent this pattern matches
            patterns: List of regex patterns
            priority: Priority for matching (higher = checked first)
        """
        self.intent_type = intent_type
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        self.priority = priority
    
    def match(self, text: str) -> Optional[Tuple[float, Dict[str, Any]]]:
        """
        Try to match text against patterns.
        
        Returns:
            Tuple of (confidence, entities) if matched, None otherwise
        """
        for pattern in self.patterns:
            match = pattern.search(text)
            if match:
                # Calculate confidence based on match quality
                confidence = min(1.0, len(match.group(0)) / len(text) + 0.5)
                entities = match.groupdict() if match.groupdict() else {}
                return (confidence, entities)
        return None


class IntentRecognizer:
    """
    Natural language intent recognition system.
    
    Features:
    - Pattern-based intent classification
    - Entity extraction
    - Confidence scoring
    - Extensible intent patterns
    """
    
    def __init__(self):
        self.patterns: List[IntentPattern] = []
        self.logger = logging.getLogger("IntentRecognizer")
        self.logger.setLevel(logging.INFO)
        
        # Initialize default patterns
        self._initialize_default_patterns()
        
        # Statistics
        self.recognition_count = 0
        self.intent_counts: Dict[str, int] = {}
        
        self.logger.info("IntentRecognizer initialized")
    
    def _initialize_default_patterns(self):
        """Initialize default intent patterns"""
        
        # Greeting patterns
        self.add_pattern(IntentPattern(
            IntentType.GREETING,
            [
                r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening)",
                r"^(what's up|how are you|howdy)"
            ],
            priority=10
        ))
        
        # Farewell patterns
        self.add_pattern(IntentPattern(
            IntentType.FAREWELL,
            [
                r"(goodbye|bye|see you|farewell|good night|take care)",
                r"(gotta go|have to leave|signing off)"
            ],
            priority=10
        ))
        
        # Help patterns
        self.add_pattern(IntentPattern(
            IntentType.HELP,
            [
                r"(help|assist|support|guide)",
                r"(how do i|how can i|what can you do)",
                r"(show me|teach me|explain)"
            ],
            priority=9
        ))
        
        # Query patterns
        self.add_pattern(IntentPattern(
            IntentType.QUERY,
            [
                r"^(what|when|where|why|who|how|which)",
                r"(tell me|show me|explain|describe)",
                r"(do you know|can you tell)"
            ],
            priority=7
        ))
        
        # Command patterns
        self.add_pattern(IntentPattern(
            IntentType.COMMAND,
            [
                r"^(create|make|build|generate|start|stop|run|execute)",
                r"^(delete|remove|cancel|abort)",
                r"^(update|modify|change|edit)",
                r"^(send|post|publish|share)"
            ],
            priority=8
        ))
        
        # Task patterns
        self.add_pattern(IntentPattern(
            IntentType.TASK,
            [
                r"(task|todo|reminder|schedule)",
                r"(add to|put on) (my )?(list|agenda|calendar)",
                r"(remind me|schedule)"
            ],
            priority=8
        ))
        
        # Affirmation patterns
        self.add_pattern(IntentPattern(
            IntentType.AFFIRMATION,
            [
                r"^(yes|yeah|yep|sure|ok|okay|correct|right|agreed)",
                r"^(absolutely|definitely|certainly|indeed)"
            ],
            priority=9
        ))
        
        # Negation patterns
        self.add_pattern(IntentPattern(
            IntentType.NEGATION,
            [
                r"^(no|nope|nah|not|never)",
                r"^(don't|do not|won't|will not|can't|cannot)",
                r"^(incorrect|wrong|false)"
            ],
            priority=9
        ))
        
        # Feedback patterns
        self.add_pattern(IntentPattern(
            IntentType.FEEDBACK,
            [
                r"(thank|thanks|appreciate)",
                r"(good|great|excellent|perfect|amazing)",
                r"(bad|poor|terrible|awful|wrong)",
                r"(improve|better|suggestion)"
            ],
            priority=6
        ))
    
    def add_pattern(self, pattern: IntentPattern):
        """Add a new intent pattern"""
        self.patterns.append(pattern)
        # Sort by priority (descending)
        self.patterns.sort(key=lambda p: p.priority, reverse=True)
        self.logger.debug(f"Added pattern for intent: {pattern.intent_type.value}")
    
    def recognize(self, text: str) -> Intent:
        """
        Recognize intent from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Intent object with type, confidence, and entities
        """
        if not text or not text.strip():
            return Intent(IntentType.UNKNOWN, 0.0, {}, text)
        
        normalized_text = text.strip()
        
        # Try to match against patterns
        for pattern in self.patterns:
            result = pattern.match(normalized_text)
            if result:
                confidence, entities = result
                intent = Intent(
                    pattern.intent_type,
                    confidence,
                    entities,
                    normalized_text
                )
                
                # Update statistics
                self.recognition_count += 1
                intent_type_str = pattern.intent_type.value
                self.intent_counts[intent_type_str] = self.intent_counts.get(intent_type_str, 0) + 1
                
                self.logger.debug(
                    f"Recognized intent: {pattern.intent_type.value} "
                    f"(confidence: {confidence:.2f})"
                )
                
                return intent
        
        # No match found
        self.recognition_count += 1
        self.intent_counts["unknown"] = self.intent_counts.get("unknown", 0) + 1
        
        return Intent(IntentType.UNKNOWN, 0.0, {}, normalized_text)
    
    def recognize_batch(self, texts: List[str]) -> List[Intent]:
        """Recognize intents for multiple texts"""
        return [self.recognize(text) for text in texts]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recognition statistics"""
        return {
            "total_recognitions": self.recognition_count,
            "intent_distribution": self.intent_counts.copy(),
            "pattern_count": len(self.patterns)
        }
    
    def add_custom_intent(self, intent_name: str, patterns: List[str], priority: int = 5):
        """
        Add a custom intent type with patterns.
        
        This is a convenience method for adding custom intents.
        Note: This creates a new IntentType dynamically.
        """
        # For simplicity, we'll map to the closest existing intent or UNKNOWN
        # In a full implementation, this would create a custom intent type
        pattern = IntentPattern(IntentType.COMMAND, patterns, priority)
        self.add_pattern(pattern)
        self.logger.info(f"Added custom intent patterns for: {intent_name}")
