"""
Persistent Memory Module

Provides cross-session memory storage for the autonomous AI agent.
Memories persist across agent restarts using JSON-backed file storage.
Supports categorized recall, relevance scoring, and automatic cleanup.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class Memory:
    """Represents a single memory entry"""
    memory_id: str
    category: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_accessed: str = ""
    access_count: int = 0
    importance: float = 0.5
    expires_at: Optional[str] = None

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.last_accessed:
            self.last_accessed = now

    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)

    def touch(self):
        """Update access metadata"""
        self.last_accessed = datetime.now().isoformat()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create Memory from dictionary"""
        return cls(**data)


class PersistentMemory:
    """
    Persistent memory system with cross-session storage.

    Features:
    - JSON-backed persistent storage
    - Categorized memory organization
    - Relevance-based recall with importance scoring
    - Automatic cleanup of expired memories
    - Memory consolidation and summarization
    - Search by category, keyword, or metadata
    """

    def __init__(self, storage_path: str = "agent_memory.json", max_memories: int = 1000):
        self.storage_path = storage_path
        self.max_memories = max_memories
        self.memories: Dict[str, Memory] = {}
        self.logger = logging.getLogger("PersistentMemory")
        self._memory_counter = 0

        # Load existing memories from disk
        self._load_from_disk()

    def store(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
        memory_id: Optional[str] = None,
    ) -> str:
        """
        Store a new memory.

        Args:
            content: The memory content to store
            category: Category for organizing memories
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            ttl_seconds: Time-to-live in seconds (None = permanent)
            memory_id: Optional custom memory ID

        Returns:
            The memory ID
        """
        importance = max(0.0, min(1.0, importance))

        self._memory_counter += 1
        mid = memory_id or f"mem-{self._memory_counter:06d}"

        expires_at = None
        if ttl_seconds is not None:
            expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()

        memory = Memory(
            memory_id=mid,
            category=category,
            content=content,
            metadata=metadata or {},
            importance=importance,
            expires_at=expires_at,
        )

        self.memories[mid] = memory

        # Evict lowest-importance memories if over capacity
        if len(self.memories) > self.max_memories:
            self._evict_least_important()

        self._save_to_disk()
        self.logger.info(f"Memory stored: {mid} (category={category})")
        return mid

    def recall(self, memory_id: str) -> Optional[Memory]:
        """
        Recall a specific memory by ID.

        Returns:
            The Memory object or None if not found/expired
        """
        if memory_id not in self.memories:
            return None

        memory = self.memories[memory_id]

        if memory.is_expired():
            del self.memories[memory_id]
            self._save_to_disk()
            return None

        memory.touch()
        self._save_to_disk()
        return memory

    def recall_by_category(self, category: str, limit: int = 10) -> List[Memory]:
        """
        Recall memories by category, sorted by importance.

        Args:
            category: The category to filter by
            limit: Maximum number of memories to return

        Returns:
            List of Memory objects
        """
        self._cleanup_expired()

        matching = [
            m for m in self.memories.values()
            if m.category == category and not m.is_expired()
        ]

        # Sort by importance (descending), then by access count
        matching.sort(key=lambda m: (m.importance, m.access_count), reverse=True)

        for m in matching[:limit]:
            m.touch()

        self._save_to_disk()
        return matching[:limit]

    def search(self, keyword: str, limit: int = 10) -> List[Memory]:
        """
        Search memories by keyword in content.

        Args:
            keyword: Search term (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching Memory objects
        """
        self._cleanup_expired()
        keyword_lower = keyword.lower()

        matching = [
            m for m in self.memories.values()
            if keyword_lower in m.content.lower() and not m.is_expired()
        ]

        matching.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        return matching[:limit]

    def forget(self, memory_id: str) -> bool:
        """
        Remove a specific memory.

        Returns:
            True if memory was removed, False if not found
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save_to_disk()
            self.logger.info(f"Memory forgotten: {memory_id}")
            return True
        return False

    def forget_category(self, category: str) -> int:
        """
        Remove all memories in a category.

        Returns:
            Number of memories removed
        """
        to_remove = [
            mid for mid, m in self.memories.items()
            if m.category == category
        ]
        for mid in to_remove:
            del self.memories[mid]

        if to_remove:
            self._save_to_disk()
            self.logger.info(f"Forgot {len(to_remove)} memories in category '{category}'")

        return len(to_remove)

    def get_summary(self) -> Dict[str, Any]:
        """Get memory system summary statistics"""
        self._cleanup_expired()

        categories: Dict[str, int] = {}
        for m in self.memories.values():
            categories[m.category] = categories.get(m.category, 0) + 1

        total = len(self.memories)
        avg_importance = (
            sum(m.importance for m in self.memories.values()) / total
            if total > 0
            else 0.0
        )

        return {
            "total_memories": total,
            "max_memories": self.max_memories,
            "categories": categories,
            "average_importance": round(avg_importance, 3),
            "storage_path": self.storage_path,
        }

    def clear(self):
        """Clear all memories"""
        self.memories.clear()
        self._memory_counter = 0
        self._save_to_disk()
        self.logger.info("All memories cleared")

    def _evict_least_important(self):
        """Evict the least important memory to make room"""
        if not self.memories:
            return

        least_important_id = min(
            self.memories,
            key=lambda mid: (
                self.memories[mid].importance,
                self.memories[mid].access_count,
            ),
        )
        del self.memories[least_important_id]
        self.logger.debug(f"Evicted memory: {least_important_id}")

    def _cleanup_expired(self):
        """Remove all expired memories"""
        expired = [
            mid for mid, m in self.memories.items()
            if m.is_expired()
        ]
        for mid in expired:
            del self.memories[mid]

        if expired:
            self._save_to_disk()

    def _save_to_disk(self):
        """Save memories to JSON file"""
        try:
            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": 1,
                "memory_counter": self._memory_counter,
                "memories": {
                    mid: m.to_dict() for mid, m in self.memories.items()
                },
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save memories: {e}")

    def _load_from_disk(self):
        """Load memories from JSON file"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            self._memory_counter = data.get("memory_counter", 0)

            for mid, mem_data in data.get("memories", {}).items():
                self.memories[mid] = Memory.from_dict(mem_data)

            self.logger.info(f"Loaded {len(self.memories)} memories from disk")

        except Exception as e:
            self.logger.error(f"Failed to load memories: {e}")
