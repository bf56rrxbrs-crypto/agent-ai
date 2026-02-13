"""
Learning System Module

This module implements auto-improving algorithms through feedback collection
and performance optimization.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class FeedbackType(Enum):
    """Types of feedback"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"


class PerformanceMetric(Enum):
    """Performance metrics to track"""
    ACCURACY = "accuracy"
    RESPONSE_TIME = "response_time"
    USER_SATISFACTION = "user_satisfaction"
    TASK_SUCCESS_RATE = "task_success_rate"


@dataclass
class FeedbackEntry:
    """User feedback entry"""
    feedback_id: str
    timestamp: datetime
    user_id: Optional[str]
    task_id: Optional[str]
    feedback_type: FeedbackType
    rating: Optional[float]  # 0.0-5.0
    comment: Optional[str]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance"""
    timestamp: datetime
    metrics: Dict[PerformanceMetric, float]
    sample_size: int


class LearningSystem:
    """
    Auto-improving learning system that collects feedback and optimizes performance.
    
    Features:
    - User feedback collection and analysis
    - Performance metric tracking
    - Trend analysis
    - Continuous improvement recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger("LearningSystem")
        self.logger.setLevel(logging.INFO)
        
        # Feedback storage
        self.feedback: List[FeedbackEntry] = []
        
        # Performance tracking
        self.performance_history: List[PerformanceSnapshot] = []
        
        # Learning parameters
        self.learning_rate = 0.01
        self.feedback_threshold = 10  # Minimum feedback for analysis
        
        self.logger.info("LearningSystem initialized")
    
    def record_feedback(
        self,
        feedback_type: FeedbackType,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> FeedbackEntry:
        """
        Record user feedback.
        
        Args:
            feedback_type: Type of feedback
            user_id: Optional user identifier
            task_id: Optional related task
            rating: Optional rating (0.0-5.0)
            comment: Optional text comment
            context: Optional contextual information
        """
        import uuid
        
        feedback_id = f"feedback-{uuid.uuid4().hex[:8]}"
        
        entry = FeedbackEntry(
            feedback_id=feedback_id,
            timestamp=datetime.now(),
            user_id=user_id,
            task_id=task_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            context=context or {}
        )
        
        self.feedback.append(entry)
        self.logger.info(f"Recorded {feedback_type.value} feedback: {feedback_id}")
        
        # Trigger learning if we have enough feedback
        if len(self.feedback) % self.feedback_threshold == 0:
            self._trigger_learning()
        
        return entry
    
    def track_performance(
        self,
        metrics: Dict[PerformanceMetric, float],
        sample_size: int = 1
    ):
        """
        Track system performance metrics.
        
        Args:
            metrics: Dictionary of metric values
            sample_size: Number of samples these metrics represent
        """
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            metrics=metrics,
            sample_size=sample_size
        )
        
        self.performance_history.append(snapshot)
        self.logger.debug(f"Tracked performance snapshot: {len(metrics)} metrics")
    
    def get_feedback_summary(
        self,
        recent_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get summary of feedback.
        
        Args:
            recent_count: Optional limit to recent feedback
        """
        feedback_to_analyze = self.feedback
        if recent_count:
            feedback_to_analyze = self.feedback[-recent_count:]
        
        if not feedback_to_analyze:
            return {
                "total": 0,
                "distribution": {},
                "average_rating": None
            }
        
        # Calculate distribution
        distribution = {}
        total_rating = 0.0
        rating_count = 0
        
        for entry in feedback_to_analyze:
            feedback_type = entry.feedback_type.value
            distribution[feedback_type] = distribution.get(feedback_type, 0) + 1
            
            if entry.rating is not None:
                total_rating += entry.rating
                rating_count += 1
        
        return {
            "total": len(feedback_to_analyze),
            "distribution": distribution,
            "average_rating": total_rating / rating_count if rating_count > 0 else None,
            "positive_ratio": distribution.get("positive", 0) / len(feedback_to_analyze)
        }
    
    def get_performance_trend(
        self,
        metric: PerformanceMetric,
        window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get performance trend for a specific metric.
        
        Args:
            metric: Metric to analyze
            window_size: Number of recent snapshots to analyze
        """
        recent_snapshots = self.performance_history[-window_size:]
        
        if not recent_snapshots:
            return {
                "metric": metric.value,
                "trend": "unknown",
                "current": None,
                "average": None
            }
        
        values = [
            snapshot.metrics.get(metric, 0.0)
            for snapshot in recent_snapshots
            if metric in snapshot.metrics
        ]
        
        if not values:
            return {
                "metric": metric.value,
                "trend": "unknown",
                "current": None,
                "average": None
            }
        
        # Calculate trend
        current = values[-1]
        average = sum(values) / len(values)
        
        if len(values) > 1:
            trend = "improving" if values[-1] > values[0] else "declining"
        else:
            trend = "stable"
        
        return {
            "metric": metric.value,
            "trend": trend,
            "current": current,
            "average": average,
            "samples": len(values)
        }
    
    def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for system improvement based on feedback and performance.
        """
        recommendations = []
        
        # Analyze feedback
        feedback_summary = self.get_feedback_summary(recent_count=50)
        
        if feedback_summary["total"] > 0:
            positive_ratio = feedback_summary["positive_ratio"]
            
            if positive_ratio < 0.5:
                recommendations.append({
                    "priority": "high",
                    "category": "user_satisfaction",
                    "issue": "Low positive feedback ratio",
                    "recommendation": "Review recent interactions and identify common pain points"
                })
            
            if feedback_summary["average_rating"] and feedback_summary["average_rating"] < 3.0:
                recommendations.append({
                    "priority": "high",
                    "category": "quality",
                    "issue": "Low average rating",
                    "recommendation": "Improve response quality and accuracy"
                })
        
        # Analyze performance trends
        for metric in PerformanceMetric:
            trend = self.get_performance_trend(metric, window_size=10)
            
            if trend["trend"] == "declining":
                recommendations.append({
                    "priority": "medium",
                    "category": "performance",
                    "issue": f"Declining {metric.value}",
                    "recommendation": f"Investigate and optimize {metric.value}"
                })
        
        return recommendations
    
    def _trigger_learning(self):
        """Trigger learning process based on accumulated feedback"""
        self.logger.info("Learning triggered - analyzing recent feedback")
        
        # In a real system, this would:
        # 1. Analyze patterns in feedback
        # 2. Adjust model parameters
        # 3. Update response strategies
        # 4. Fine-tune algorithms
        
        recommendations = self.get_improvement_recommendations()
        if recommendations:
            self.logger.info(f"Generated {len(recommendations)} improvement recommendations")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        return {
            "total_feedback": len(self.feedback),
            "feedback_summary": self.get_feedback_summary(),
            "performance_snapshots": len(self.performance_history),
            "learning_rate": self.learning_rate,
            "recommendations_count": len(self.get_improvement_recommendations())
        }
    
    def export_feedback(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export feedback entries"""
        entries = self.feedback
        
        if user_id:
            entries = [f for f in entries if f.user_id == user_id]
        
        return [
            {
                "feedback_id": entry.feedback_id,
                "timestamp": entry.timestamp.isoformat(),
                "user_id": entry.user_id,
                "feedback_type": entry.feedback_type.value,
                "rating": entry.rating,
                "comment": entry.comment
            }
            for entry in entries
        ]
