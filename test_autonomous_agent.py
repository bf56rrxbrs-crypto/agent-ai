"""
Unit tests for the Autonomous Agent module.
"""

import unittest
import asyncio
from datetime import datetime

from autonomous_agent import AutonomousAgent, Task, TaskPriority, AgentState


class TestAutonomousAgent(unittest.TestCase):
    """Test cases for AutonomousAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = AutonomousAgent("test-agent-001")
    
    def test_agent_initialization(self):
        """Test agent is initialized correctly"""
        self.assertEqual(self.agent.agent_id, "test-agent-001")
        self.assertEqual(self.agent.state, AgentState.IDLE)
        self.assertEqual(len(self.agent.task_queue), 0)
    
    def test_add_task(self):
        """Test adding tasks to queue"""
        async def dummy_action(**kwargs):
            return "done"
        
        task = Task(
            task_id="test-task-001",
            name="Test Task",
            priority=TaskPriority.MEDIUM,
            action=dummy_action,
            params={},
            created_at=datetime.now()
        )
        
        self.agent.add_task(task)
        self.assertEqual(len(self.agent.task_queue), 1)
    
    def test_task_priority_ordering(self):
        """Test tasks are ordered by priority"""
        async def dummy_action(**kwargs):
            return "done"
        
        low_task = Task(
            task_id="low",
            name="Low Priority",
            priority=TaskPriority.LOW,
            action=dummy_action,
            params={},
            created_at=datetime.now()
        )
        
        high_task = Task(
            task_id="high",
            name="High Priority",
            priority=TaskPriority.HIGH,
            action=dummy_action,
            params={},
            created_at=datetime.now()
        )
        
        self.agent.add_task(low_task)
        self.agent.add_task(high_task)
        
        # High priority should be first
        self.assertEqual(self.agent.task_queue[0].task_id, "high")
        self.assertEqual(self.agent.task_queue[1].task_id, "low")
    
    def test_get_status(self):
        """Test getting agent status"""
        status = self.agent.get_status()
        
        self.assertIn("agent_id", status)
        self.assertIn("state", status)
        self.assertIn("health", status)
        self.assertIn("queue_size", status)
        self.assertEqual(status["agent_id"], "test-agent-001")
    
    def test_event_handler_registration(self):
        """Test registering event handlers"""
        handler_called = False
        
        def test_handler(data):
            nonlocal handler_called
            handler_called = True
        
        self.agent.on("test_event", test_handler)
        self.assertIn("test_event", self.agent.event_handlers)
    
    async def test_task_execution(self):
        """Test task execution"""
        result_container = []
        
        async def test_action(**kwargs):
            result_container.append("executed")
            return "success"
        
        task = Task(
            task_id="exec-test",
            name="Execution Test",
            priority=TaskPriority.HIGH,
            action=test_action,
            params={},
            created_at=datetime.now()
        )
        
        await self.agent._execute_task(task)
        
        self.assertEqual(len(result_container), 1)
        self.assertIn("exec-test", self.agent.completed_tasks)
    
    async def test_start_stop(self):
        """Test starting and stopping agent"""
        await self.agent.start()
        self.assertEqual(self.agent.state, AgentState.ACTIVE)
        
        await self.agent.stop()
        self.assertEqual(self.agent.state, AgentState.SHUTDOWN)


def async_test(coro):
    """Decorator to run async tests"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper


# Apply decorator to async test methods
TestAutonomousAgent.test_task_execution = async_test(
    TestAutonomousAgent.test_task_execution
)
TestAutonomousAgent.test_start_stop = async_test(
    TestAutonomousAgent.test_start_stop
)


if __name__ == "__main__":
    unittest.main()
