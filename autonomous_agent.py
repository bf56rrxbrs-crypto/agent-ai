"""
Autonomous Agent Core Module

This module provides the core functionality for an autonomous AI agent with
self-monitoring, decision-making, and task execution capabilities.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a task for the autonomous agent"""
    task_id: str
    name: str
    priority: TaskPriority
    action: Callable
    params: Dict[str, Any]
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


class AutonomousAgent:
    """
    Core autonomous agent with self-monitoring and task execution capabilities.
    
    Features:
    - Autonomous task scheduling and execution
    - Self-monitoring and health checks
    - Error recovery with retry mechanisms
    - Priority-based task queue
    - Event-driven architecture
    """
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.state = AgentState.IDLE
        self.task_queue: List[Task] = []
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"AutonomousAgent-{agent_id}")
        self.logger.setLevel(logging.INFO)
        
        # Health monitoring
        self.health_status = {
            "is_healthy": True,
            "last_check": datetime.now(),
            "error_count": 0,
            "uptime_seconds": 0
        }
        
        self.logger.info(f"Autonomous agent {agent_id} initialized")
    
    async def start(self):
        """Start the autonomous agent"""
        self.state = AgentState.ACTIVE
        self.logger.info(f"Agent {self.agent_id} started")
        await self._emit_event("agent_started", {"agent_id": self.agent_id})
        
        # Start monitoring task
        asyncio.create_task(self._health_monitor())
        
        # Start task processor
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop the autonomous agent gracefully"""
        self.state = AgentState.SHUTDOWN
        self.logger.info(f"Agent {self.agent_id} shutting down")
        await self._emit_event("agent_stopped", {"agent_id": self.agent_id})
    
    def add_task(self, task: Task):
        """Add a task to the execution queue"""
        self.task_queue.append(task)
        # Sort by priority
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
        self.logger.info(f"Task {task.task_id} added to queue with priority {task.priority.name}")
    
    async def _process_tasks(self):
        """Process tasks from the queue autonomously"""
        while self.state == AgentState.ACTIVE:
            if self.task_queue:
                task = self.task_queue.pop(0)
                await self._execute_task(task)
            else:
                await asyncio.sleep(1)  # Wait before checking again
    
    async def _execute_task(self, task: Task):
        """Execute a single task with error handling and retry logic"""
        try:
            self.logger.info(f"Executing task {task.task_id}: {task.name}")
            await self._emit_event("task_started", {"task_id": task.task_id})
            
            # Execute the task action
            if asyncio.iscoroutinefunction(task.action):
                result = await task.action(**task.params)
            else:
                result = task.action(**task.params)
            
            self.completed_tasks.append(task.task_id)
            self.logger.info(f"Task {task.task_id} completed successfully")
            await self._emit_event("task_completed", {
                "task_id": task.task_id,
                "result": result
            })
            
        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {str(e)}")
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                # Retry with exponential backoff
                wait_time = 2 ** task.retry_count
                self.logger.info(f"Retrying task {task.task_id} in {wait_time} seconds")
                await asyncio.sleep(wait_time)
                self.task_queue.insert(0, task)  # Re-add to front of queue
            else:
                self.failed_tasks.append(task.task_id)
                self.health_status["error_count"] += 1
                await self._emit_event("task_failed", {
                    "task_id": task.task_id,
                    "error": str(e)
                })
    
    async def _health_monitor(self):
        """Continuous health monitoring"""
        start_time = datetime.now()
        
        while self.state == AgentState.ACTIVE:
            self.health_status["last_check"] = datetime.now()
            self.health_status["uptime_seconds"] = (
                datetime.now() - start_time
            ).total_seconds()
            
            # Check health criteria
            error_rate = len(self.failed_tasks) / max(
                len(self.completed_tasks) + len(self.failed_tasks), 1
            )
            
            if error_rate > 0.5:
                self.health_status["is_healthy"] = False
                self.logger.warning("Agent health degraded - high error rate")
                await self._emit_event("health_degraded", {
                    "error_rate": error_rate
                })
            else:
                self.health_status["is_healthy"] = True
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    def on(self, event_name: str, handler: Callable):
        """Register an event handler"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Event handler registered for {event_name}")
    
    async def _emit_event(self, event_name: str, data: Dict[str, Any]):
        """Emit an event to all registered handlers"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_name}: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "health": self.health_status,
            "queue_size": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks)
        }
