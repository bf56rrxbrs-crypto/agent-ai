"""
Emotion Analysis Module

This module provides sentiment analysis and emotion detection capabilities
to modify responses based on user emotions.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class Emotion(Enum):
    """Primary emotions"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class Sentiment(Enum):
    """Sentiment categories"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class EmotionAnalysis:
    """Result of emotion analysis"""
    text: str
    primary_emotion: Emotion
    emotion_scores: Dict[Emotion, float]
    sentiment: Sentiment
    sentiment_score: float  # -1.0 to 1.0
    confidence: float


class EmotionAnalyzer:
    """
    Emotion and sentiment analysis system.
    
    Features:
    - Emotion detection from text
    - Sentiment analysis
    - Emotion-based response modification
    - Emotional intelligence integration
    
    Note: This is a simplified implementation using keyword matching.
    Production systems would use ML models like BERT, etc.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("EmotionAnalyzer")
        self.logger.setLevel(logging.INFO)
        
        # Initialize emotion keywords
        self._initialize_emotion_keywords()
        
        # Analysis history
        self.analysis_history: List[EmotionAnalysis] = []
        
        self.logger.info("EmotionAnalyzer initialized")
    
    def _initialize_emotion_keywords(self):
        """Initialize keyword sets for emotion detection"""
        self.emotion_keywords = {
            Emotion.JOY: {
                "happy", "joy", "delighted", "excited", "wonderful", "great",
                "awesome", "fantastic", "amazing", "love", "glad", "pleased",
                "cheerful", "thrilled", "ecstatic", "😊", "😃", "😄", "🎉"
            },
            Emotion.SADNESS: {
                "sad", "unhappy", "depressed", "disappointed", "miserable",
                "sorrow", "grief", "heartbroken", "lonely", "down", "blue",
                "crying", "tears", "😢", "😭", "☹️"
            },
            Emotion.ANGER: {
                "angry", "mad", "furious", "irritated", "annoyed", "rage",
                "frustrated", "outraged", "hostile", "bitter", "resentful",
                "hate", "😠", "😡", "🤬"
            },
            Emotion.FEAR: {
                "afraid", "scared", "frightened", "terrified", "anxious",
                "worried", "nervous", "panic", "dread", "horrified",
                "😨", "😰", "😱"
            },
            Emotion.SURPRISE: {
                "surprised", "shocked", "amazed", "astonished", "stunned",
                "wow", "unexpected", "incredible", "unbelievable", "😲", "😮"
            },
            Emotion.DISGUST: {
                "disgusted", "revolted", "sick", "nauseated", "gross",
                "horrible", "awful", "terrible", "yuck", "🤢", "🤮"
            }
        }
        
        self.positive_keywords = {
            "good", "great", "excellent", "wonderful", "fantastic", "amazing",
            "perfect", "beautiful", "lovely", "nice", "best", "awesome",
            "brilliant", "outstanding", "superb", "terrific"
        }
        
        self.negative_keywords = {
            "bad", "poor", "awful", "terrible", "horrible", "worst",
            "disappointing", "useless", "pathetic", "inadequate", "inferior",
            "deficient", "unsatisfactory", "unacceptable"
        }
    
    def analyze_emotion(self, text: str) -> EmotionAnalysis:
        """
        Analyze emotions in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            EmotionAnalysis with detected emotions and sentiment
        """
        text_lower = text.lower()
        
        # Calculate emotion scores
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by text length
            emotion_scores[emotion] = score / max(len(text.split()), 1)
        
        # Determine primary emotion
        if not any(emotion_scores.values()):
            primary_emotion = Emotion.NEUTRAL
            confidence = 1.0
        else:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            confidence = emotion_scores[primary_emotion]
        
        # Calculate sentiment
        sentiment_score, sentiment = self._calculate_sentiment(text_lower)
        
        analysis = EmotionAnalysis(
            text=text,
            primary_emotion=primary_emotion,
            emotion_scores=emotion_scores,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            confidence=min(confidence, 1.0)
        )
        
        self.analysis_history.append(analysis)
        self.logger.debug(f"Analyzed emotion: {primary_emotion.value}, sentiment: {sentiment.value}")
        
        return analysis
    
    def _calculate_sentiment(self, text: str) -> tuple[float, Sentiment]:
        """Calculate sentiment score and category"""
        positive_count = sum(1 for word in self.positive_keywords if word in text)
        negative_count = sum(1 for word in self.negative_keywords if word in text)
        
        # Calculate score (-1.0 to 1.0)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        # Determine category
        if score > 0.5:
            sentiment = Sentiment.VERY_POSITIVE
        elif score > 0.1:
            sentiment = Sentiment.POSITIVE
        elif score < -0.5:
            sentiment = Sentiment.VERY_NEGATIVE
        elif score < -0.1:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL
        
        return score, sentiment
    
    def modify_response_for_emotion(
        self,
        original_response: str,
        user_emotion: Emotion
    ) -> str:
        """
        Modify response based on detected user emotion.
        
        Args:
            original_response: Original response text
            user_emotion: Detected user emotion
            
        Returns:
            Modified response appropriate for the emotion
        """
        modified = original_response
        
        if user_emotion == Emotion.SADNESS:
            # Add empathetic language
            if not any(word in modified.lower() for word in ["sorry", "understand"]):
                modified = f"I understand this may be difficult. {modified}"
        
        elif user_emotion == Emotion.ANGER:
            # Add calming language
            modified = f"I apologize for any frustration. {modified}"
            # Remove exclamation marks
            modified = modified.replace("!", ".")
        
        elif user_emotion == Emotion.JOY:
            # Add enthusiastic response
            if "!" not in modified:
                modified = modified.replace(".", "!", 1)
        
        elif user_emotion == Emotion.FEAR:
            # Add reassuring language
            modified = f"Don't worry, I'm here to help. {modified}"
        
        return modified
    
    def analyze_conversation_mood(
        self,
        recent_messages: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze overall mood of a conversation.
        
        Args:
            recent_messages: List of recent messages
            
        Returns:
            Dictionary with mood analysis
        """
        if not recent_messages:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "dominant_emotion": "neutral",
                "mood_trend": "stable"
            }
        
        analyses = [self.analyze_emotion(msg) for msg in recent_messages]
        
        # Calculate average sentiment
        avg_sentiment = sum(a.sentiment_score for a in analyses) / len(analyses)
        
        # Find dominant emotion
        emotion_counts = {}
        for analysis in analyses:
            emotion = analysis.primary_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        # Determine trend
        if len(analyses) > 1:
            recent_avg = sum(a.sentiment_score for a in analyses[-3:]) / min(3, len(analyses))
            earlier_avg = sum(a.sentiment_score for a in analyses[:-3]) / max(1, len(analyses) - 3)
            
            if recent_avg > earlier_avg + 0.2:
                trend = "improving"
            elif recent_avg < earlier_avg - 0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "overall_sentiment": self._score_to_sentiment(avg_sentiment),
            "sentiment_score": avg_sentiment,
            "dominant_emotion": dominant_emotion,
            "mood_trend": trend,
            "message_count": len(recent_messages)
        }
    
    def _score_to_sentiment(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.5:
            return "very positive"
        elif score > 0.1:
            return "positive"
        elif score < -0.5:
            return "very negative"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get emotion analysis statistics"""
        if not self.analysis_history:
            return {
                "total_analyses": 0,
                "emotion_distribution": {},
                "sentiment_distribution": {},
                "average_sentiment": 0.0
            }
        
        emotion_dist = {}
        sentiment_dist = {}
        total_sentiment = 0.0
        
        for analysis in self.analysis_history:
            emotion = analysis.primary_emotion.value
            sentiment = analysis.sentiment.value
            
            emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
            total_sentiment += analysis.sentiment_score
        
        return {
            "total_analyses": len(self.analysis_history),
            "emotion_distribution": emotion_dist,
            "sentiment_distribution": sentiment_dist,
            "average_sentiment": total_sentiment / len(self.analysis_history)
        }
