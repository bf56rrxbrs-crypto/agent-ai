"""
Context Manager Module

This module manages conversation context to maintain state and provide
consistency across multiple interactions.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class ConversationContext:
    """Represents context for a conversation"""
    context_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Context data
    history: List[Dict[str, Any]] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # State tracking
    last_intent: Optional[str] = None
    turn_count: int = 0
    
    def add_turn(self, user_input: str, agent_response: str, intent: Optional[str] = None):
        """Add a conversation turn"""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "intent": intent,
            "turn_number": self.turn_count
        }
        self.history.append(turn)
        self.turn_count += 1
        self.last_updated = datetime.now()
        if intent:
            self.last_intent = intent
    
    def add_entity(self, entity_type: str, value: Any):
        """Add or update an entity in context"""
        self.entities[entity_type] = value
        self.last_updated = datetime.now()
    
    def add_topic(self, topic: str):
        """Add a topic to the conversation"""
        if topic not in self.topics:
            self.topics.append(topic)
            self.last_updated = datetime.now()
    
    def get_recent_history(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation turns"""
        return self.history[-count:] if self.history else []
    
    def clear_history(self):
        """Clear conversation history but keep entities"""
        self.history.clear()
        self.turn_count = 0
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "context_id": self.context_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "turn_count": self.turn_count,
            "last_intent": self.last_intent,
            "entities": self.entities,
            "topics": self.topics,
            "history_length": len(self.history),
            "metadata": self.metadata
        }


class ContextManager:
    """
    Manages conversation contexts for maintaining state across interactions.
    
    Features:
    - Multi-user context management
    - Session-based context isolation
    - Entity and topic tracking
    - Conversation history
    - Context expiration
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize context manager.
        
        Args:
            default_ttl: Default time-to-live for contexts in seconds
        """
        self.contexts: Dict[str, ConversationContext] = {}
        self.default_ttl = default_ttl
        self.logger = logging.getLogger("ContextManager")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("ContextManager initialized")
    
    def create_context(
        self,
        context_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """Create a new conversation context"""
        context = ConversationContext(
            context_id=context_id,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        self.contexts[context_id] = context
        self.logger.info(f"Created context: {context_id}")
        
        return context
    
    def get_context(self, context_id: str) -> Optional[ConversationContext]:
        """Get a context by ID"""
        context = self.contexts.get(context_id)
        
        if context:
            # Check if context has expired
            if self._is_expired(context):
                self.logger.info(f"Context {context_id} expired, removing")
                self.delete_context(context_id)
                return None
        
        return context
    
    def get_or_create_context(
        self,
        context_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ConversationContext:
        """Get existing context or create new one"""
        context = self.get_context(context_id)
        
        if not context:
            context = self.create_context(context_id, user_id, session_id)
        
        return context
    
    def delete_context(self, context_id: str) -> bool:
        """Delete a context"""
        if context_id in self.contexts:
            del self.contexts[context_id]
            self.logger.info(f"Deleted context: {context_id}")
            return True
        return False
    
    def update_context(
        self,
        context_id: str,
        user_input: str,
        agent_response: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        topics: Optional[List[str]] = None
    ):
        """Update context with new conversation turn"""
        context = self.get_context(context_id)
        
        if not context:
            self.logger.warning(f"Context {context_id} not found, creating new")
            context = self.create_context(context_id)
        
        # Add conversation turn
        context.add_turn(user_input, agent_response, intent)
        
        # Update entities
        if entities:
            for entity_type, value in entities.items():
                context.add_entity(entity_type, value)
        
        # Update topics
        if topics:
            for topic in topics:
                context.add_topic(topic)
        
        self.logger.debug(f"Updated context {context_id} (turn {context.turn_count})")
    
    def get_context_summary(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the context"""
        context = self.get_context(context_id)
        
        if not context:
            return None
        
        recent_history = context.get_recent_history(3)
        
        return {
            "context_id": context.context_id,
            "turn_count": context.turn_count,
            "last_intent": context.last_intent,
            "entities": context.entities,
            "topics": context.topics,
            "recent_turns": recent_history,
            "age_seconds": (datetime.now() - context.created_at).total_seconds()
        }
    
    def list_contexts(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all contexts, optionally filtered by user"""
        contexts = []
        
        for context in self.contexts.values():
            if user_id and context.user_id != user_id:
                continue
            
            contexts.append({
                "context_id": context.context_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "turn_count": context.turn_count,
                "created_at": context.created_at.isoformat(),
                "last_updated": context.last_updated.isoformat()
            })
        
        return contexts
    
    def cleanup_expired(self) -> int:
        """Remove expired contexts"""
        expired_ids = [
            context_id
            for context_id, context in self.contexts.items()
            if self._is_expired(context)
        ]
        
        for context_id in expired_ids:
            self.delete_context(context_id)
        
        if expired_ids:
            self.logger.info(f"Cleaned up {len(expired_ids)} expired contexts")
        
        return len(expired_ids)
    
    def _is_expired(self, context: ConversationContext) -> bool:
        """Check if a context has expired"""
        age = datetime.now() - context.last_updated
        return age > timedelta(seconds=self.default_ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        total_turns = sum(ctx.turn_count for ctx in self.contexts.values())
        active_contexts = len(self.contexts)
        
        # Calculate average age
        if self.contexts:
            avg_age = sum(
                (datetime.now() - ctx.created_at).total_seconds()
                for ctx in self.contexts.values()
            ) / len(self.contexts)
        else:
            avg_age = 0
        
        return {
            "active_contexts": active_contexts,
            "total_turns": total_turns,
            "average_turns_per_context": total_turns / active_contexts if active_contexts > 0 else 0,
            "average_context_age_seconds": avg_age,
            "ttl_seconds": self.default_ttl
        }
    
    def merge_contexts(self, source_id: str, target_id: str) -> bool:
        """Merge one context into another"""
        source = self.get_context(source_id)
        target = self.get_context(target_id)
        
        if not source or not target:
            return False
        
        # Merge history
        target.history.extend(source.history)
        target.turn_count += source.turn_count
        
        # Merge entities (target takes precedence)
        for key, value in source.entities.items():
            if key not in target.entities:
                target.entities[key] = value
        
        # Merge topics
        for topic in source.topics:
            if topic not in target.topics:
                target.topics.append(topic)
        
        # Update timestamp
        target.last_updated = datetime.now()
        
        # Delete source context
        self.delete_context(source_id)
        
        self.logger.info(f"Merged context {source_id} into {target_id}")
        return True
