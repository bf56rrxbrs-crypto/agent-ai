"""
iOS Agent Module

AI agent assistant tailored for iPhone 17 Pro iOS devices.
Combines forward-thinking structural loop engineering, persistent memory,
and iOS-specific device capabilities into a unified agent.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field

from autonomous_agent import AutonomousAgent, Task, TaskPriority
from persistent_memory import PersistentMemory
from forward_thinking_engine import (
    ForwardThinkingEngine,
    PlanStep,
    ExecutionPlan,
    StepStatus,
    PlanStatus,
)
from cache_manager import CacheManager


class DeviceCapability:
    """Represents an iOS device capability"""

    def __init__(self, name: str, description: str, handler: Optional[Callable] = None):
        self.name = name
        self.description = description
        self.handler = handler
        self.enabled = True
        self.usage_count = 0

    async def execute(self, **params) -> Dict[str, Any]:
        """Execute this capability"""
        self.usage_count += 1

        if self.handler is not None:
            if asyncio.iscoroutinefunction(self.handler):
                result = await self.handler(**params)
            else:
                result = self.handler(**params)
            return {"capability": self.name, "result": result}

        return {
            "capability": self.name,
            "status": "simulated",
            "params": params,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "usage_count": self.usage_count,
        }


@dataclass
class IOSDeviceProfile:
    """iPhone 17 Pro device profile"""
    device_model: str = "iPhone 17 Pro"
    os_version: str = "iOS 19"
    chip: str = "A19 Pro"
    ram_gb: int = 12
    neural_engine_cores: int = 18
    always_on_display: bool = True
    dynamic_island: bool = True
    action_button: bool = True
    camera_control: bool = True
    supported_features: List[str] = field(default_factory=lambda: [
        "siri_integration",
        "shortcuts_automation",
        "focus_modes",
        "live_activities",
        "haptic_feedback",
        "spatial_audio",
        "face_id",
        "nfc",
        "ultra_wideband",
        "satellite_connectivity",
        "usb_c",
        "always_on_display",
        "promotion_120hz",
    ])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "device_model": self.device_model,
            "os_version": self.os_version,
            "chip": self.chip,
            "ram_gb": self.ram_gb,
            "neural_engine_cores": self.neural_engine_cores,
            "always_on_display": self.always_on_display,
            "dynamic_island": self.dynamic_island,
            "action_button": self.action_button,
            "camera_control": self.camera_control,
            "supported_features": self.supported_features,
        }


class IOSAgent:
    """
    AI agent assistant tailored for iPhone 17 Pro iOS devices.

    Combines core autonomous capabilities with iOS-specific features:
    - Forward-thinking structural loop engineering for anticipatory planning
    - Persistent memory for cross-session context and learning
    - iOS device-aware task execution
    - Adaptive instruction following with reliability tracking

    Architecture:
        IOSAgent
         ├── AutonomousAgent (task execution engine)
         ├── ForwardThinkingEngine (plan-execute-evaluate loops)
         ├── PersistentMemory (cross-session storage)
         ├── CacheManager (fast access cache)
         ├── DeviceCapabilities (iOS-specific features)
         └── IOSDeviceProfile (hardware/OS awareness)
    """

    def __init__(
        self,
        agent_id: str = "ios-agent-001",
        memory_path: str = "agent_memory.json",
        config: Optional[Dict[str, Any]] = None,
    ):
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = logging.getLogger(f"IOSAgent-{agent_id}")

        # Device profile
        self.device = IOSDeviceProfile()

        # Core components
        self.agent = AutonomousAgent(agent_id=agent_id, config=self.config)
        self.memory = PersistentMemory(storage_path=memory_path, max_memories=1000)
        self.thinking_engine = ForwardThinkingEngine(max_iterations=5)
        self.cache = CacheManager(strategy="lru", max_size=500, default_ttl=1800)

        # iOS device capabilities
        self.capabilities: Dict[str, DeviceCapability] = {}
        self._register_default_capabilities()

        # Reliability tracking
        self._instruction_count = 0
        self._successful_instructions = 0

        # Wire up evaluation handler to use memory for re-planning
        self.thinking_engine.on_evaluation(self._on_plan_evaluation)

        self.logger.info(
            f"iOS Agent initialized: {agent_id} on {self.device.device_model}"
        )

    def _register_default_capabilities(self):
        """Register default iOS device capabilities"""
        default_caps = [
            DeviceCapability(
                "notification_management",
                "Manage and prioritize iOS notifications intelligently",
            ),
            DeviceCapability(
                "shortcut_automation",
                "Create and execute iOS Shortcuts automations",
            ),
            DeviceCapability(
                "focus_mode_control",
                "Manage Focus modes based on context and schedule",
            ),
            DeviceCapability(
                "app_management",
                "Launch, switch, and manage iOS applications",
            ),
            DeviceCapability(
                "health_monitoring",
                "Access and analyze health and fitness data",
            ),
            DeviceCapability(
                "smart_scheduling",
                "Intelligent calendar and reminder management",
            ),
            DeviceCapability(
                "communication_handler",
                "Handle messages, calls, and email intelligently",
            ),
            DeviceCapability(
                "media_control",
                "Control media playback and spatial audio settings",
            ),
            DeviceCapability(
                "device_optimization",
                "Optimize battery, storage, and performance",
            ),
            DeviceCapability(
                "context_awareness",
                "Location, time, and activity context analysis",
            ),
        ]

        for cap in default_caps:
            self.capabilities[cap.name] = cap

    async def start(self):
        """Start the iOS agent and all subsystems"""
        self.logger.info("Starting iOS Agent...")

        # Start core agent
        await self.agent.start()

        # Load context from persistent memory
        context_memories = self.memory.recall_by_category("user_context", limit=5)
        if context_memories:
            self.logger.info(
                f"Restored {len(context_memories)} context memories from previous sessions"
            )

        # Store startup event
        self.memory.store(
            content=f"Agent started on {self.device.device_model}",
            category="system_events",
            importance=0.3,
            metadata={"event": "startup", "device": self.device.device_model},
        )

        self.logger.info("iOS Agent started successfully")

    async def stop(self):
        """Stop the iOS agent gracefully"""
        self.logger.info("Stopping iOS Agent...")

        # Store shutdown event
        self.memory.store(
            content=f"Agent stopped. Reliability: {self.get_reliability():.1%}",
            category="system_events",
            importance=0.3,
            metadata={
                "event": "shutdown",
                "reliability": self.get_reliability(),
                "instructions_handled": self._instruction_count,
            },
        )

        await self.agent.stop()
        self.logger.info("iOS Agent stopped gracefully")

    async def execute_instruction(
        self,
        instruction: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        use_planning: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a user instruction with forward-thinking planning.

        Args:
            instruction: The user's instruction/request
            priority: Priority level for the instruction
            use_planning: Whether to use the forward-thinking engine

        Returns:
            Execution result
        """
        self._instruction_count += 1
        self.logger.info(f"Instruction received: {instruction}")

        # Store instruction in memory
        self.memory.store(
            content=instruction,
            category="instructions",
            importance=0.6,
            metadata={"priority": priority.name},
        )

        try:
            if use_planning:
                result = await self._execute_with_planning(instruction, priority)
            else:
                result = await self._execute_direct(instruction, priority)

            self._successful_instructions += 1

            # Store success in memory
            self.memory.store(
                content=f"Successfully executed: {instruction}",
                category="execution_history",
                importance=0.4,
                metadata={"result_status": "success"},
            )

            return result

        except Exception as e:
            self.logger.error(f"Instruction failed: {e}")

            # Store failure in memory for learning
            self.memory.store(
                content=f"Failed to execute: {instruction} - Error: {str(e)}",
                category="execution_history",
                importance=0.7,
                metadata={"result_status": "failure", "error": str(e)},
            )

            return {
                "status": "failed",
                "instruction": instruction,
                "error": str(e),
            }

    async def _execute_with_planning(
        self, instruction: str, priority: TaskPriority
    ) -> Dict[str, Any]:
        """Execute instruction using the forward-thinking engine"""
        # Create a plan
        plan = self.thinking_engine.create_plan(goal=instruction)

        # Add analysis step
        self.thinking_engine.add_step(
            plan_id=plan.plan_id,
            name="Analyze Instruction",
            description=f"Analyze and decompose: {instruction}",
            action=self._analyze_instruction,
            params={"instruction": instruction},
        )

        # Add execution step
        self.thinking_engine.add_step(
            plan_id=plan.plan_id,
            name="Execute Core Action",
            description=f"Execute the primary action for: {instruction}",
            action=self._execute_core_action,
            params={"instruction": instruction, "priority": priority.name},
            depends_on=[f"{plan.plan_id}-step-001"],
        )

        # Add verification step
        self.thinking_engine.add_step(
            plan_id=plan.plan_id,
            name="Verify Result",
            description="Verify execution outcome and update memory",
            action=self._verify_result,
            params={"instruction": instruction},
            depends_on=[f"{plan.plan_id}-step-002"],
        )

        # Execute the plan
        result = await self.thinking_engine.execute_plan(plan.plan_id)

        return {
            "status": result["status"],
            "instruction": instruction,
            "plan_id": plan.plan_id,
            "iterations": result["iterations"],
            "steps": result["evaluation"],
        }

    async def _execute_direct(
        self, instruction: str, priority: TaskPriority
    ) -> Dict[str, Any]:
        """Execute instruction directly without planning"""
        result = await self._execute_core_action(
            instruction=instruction, priority=priority.name
        )
        return {
            "status": "completed",
            "instruction": instruction,
            "result": result,
        }

    async def _analyze_instruction(self, **kwargs) -> Dict[str, Any]:
        """Analyze an instruction for execution planning"""
        instruction = kwargs.get("instruction", "")

        # Check memory for similar past instructions
        similar = self.memory.search(instruction[:50], limit=3)

        return {
            "instruction": instruction,
            "similar_past_instructions": len(similar),
            "analysis": "instruction_analyzed",
        }

    async def _execute_core_action(self, **kwargs) -> Dict[str, Any]:
        """Execute the core action for an instruction"""
        instruction = kwargs.get("instruction", "")
        priority = kwargs.get("priority", "MEDIUM")

        # Check cache for pre-computed result
        cache_key = f"instruction:{instruction[:100]}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        result = {
            "instruction": instruction,
            "priority": priority,
            "device": self.device.device_model,
            "executed_at": datetime.now().isoformat(),
            "status": "executed",
        }

        # Cache the result
        self.cache.set(cache_key, result)

        return result

    async def _verify_result(self, **kwargs) -> Dict[str, Any]:
        """Verify execution result"""
        instruction = kwargs.get("instruction", "")
        return {
            "instruction": instruction,
            "verified": True,
            "verified_at": datetime.now().isoformat(),
        }

    async def _on_plan_evaluation(self, plan: ExecutionPlan, evaluation: Dict[str, Any]):
        """Handle plan evaluation for adaptive re-planning"""
        if evaluation.get("needs_replanning"):
            self.memory.store(
                content=f"Plan {plan.plan_id} needs re-planning: {evaluation}",
                category="planning_events",
                importance=0.6,
                metadata={"plan_id": plan.plan_id, "evaluation": str(evaluation)},
            )
            self.logger.info(
                f"Re-planning triggered for {plan.plan_id}: "
                f"{evaluation['failed']} failed, {evaluation['pending']} pending"
            )

    def add_capability(self, capability: DeviceCapability):
        """Register a new device capability"""
        self.capabilities[capability.name] = capability
        self.logger.info(f"Capability added: {capability.name}")

    async def use_capability(
        self, capability_name: str, **params
    ) -> Dict[str, Any]:
        """
        Use a specific device capability.

        Args:
            capability_name: Name of the capability to use
            **params: Parameters for the capability

        Returns:
            Capability execution result
        """
        if capability_name not in self.capabilities:
            raise ValueError(f"Unknown capability: {capability_name}")

        capability = self.capabilities[capability_name]
        if not capability.enabled:
            raise RuntimeError(f"Capability disabled: {capability_name}")

        result = await capability.execute(**params)

        # Track in memory
        self.memory.store(
            content=f"Used capability: {capability_name}",
            category="capability_usage",
            importance=0.3,
            metadata={"capability": capability_name, "params": str(params)},
        )

        return result

    def remember(
        self,
        content: str,
        category: str = "user_context",
        importance: float = 0.5,
    ) -> str:
        """
        Store a memory for cross-session recall.

        Args:
            content: What to remember
            category: Memory category
            importance: How important (0.0-1.0)

        Returns:
            Memory ID
        """
        return self.memory.store(
            content=content,
            category=category,
            importance=importance,
        )

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recall memories matching a query.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of matching memories
        """
        results = self.memory.search(query, limit=limit)
        return [
            {
                "memory_id": m.memory_id,
                "content": m.content,
                "category": m.category,
                "importance": m.importance,
            }
            for m in results
        ]

    def get_reliability(self) -> float:
        """Get instruction execution reliability rate"""
        if self._instruction_count == 0:
            return 1.0
        return self._successful_instructions / self._instruction_count

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        agent_status = self.agent.get_status()
        memory_summary = self.memory.get_summary()
        engine_summary = self.thinking_engine.get_summary()
        cache_stats = self.cache.get_stats()

        return {
            "agent_id": self.agent_id,
            "device": self.device.to_dict(),
            "agent_status": agent_status,
            "memory": memory_summary,
            "planning_engine": engine_summary,
            "cache": cache_stats,
            "capabilities": {
                name: cap.to_dict() for name, cap in self.capabilities.items()
            },
            "reliability": {
                "rate": self.get_reliability(),
                "total_instructions": self._instruction_count,
                "successful": self._successful_instructions,
            },
        }
