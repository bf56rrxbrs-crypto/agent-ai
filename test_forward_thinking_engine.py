"""
Unit tests for the Forward-Thinking Structural Loop Engine.
"""

import unittest
import asyncio
from forward_thinking_engine import (
    ForwardThinkingEngine,
    PlanStep,
    ExecutionPlan,
    StepStatus,
    PlanStatus,
)


def async_test(coro):
    """Decorator to run async tests"""
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper


class TestPlanStep(unittest.TestCase):
    """Test cases for PlanStep"""

    def test_step_creation(self):
        """Test creating a plan step"""
        step = PlanStep(
            step_id="step-001",
            name="Test Step",
            description="A test step",
        )
        self.assertEqual(step.step_id, "step-001")
        self.assertEqual(step.status, StepStatus.PENDING)

    def test_step_to_dict(self):
        """Test step serialization"""
        step = PlanStep(
            step_id="step-002",
            name="Serialize Step",
            description="Test serialization",
            params={"key": "value"},
        )
        data = step.to_dict()
        self.assertEqual(data["step_id"], "step-002")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["params"], {"key": "value"})


class TestExecutionPlan(unittest.TestCase):
    """Test cases for ExecutionPlan"""

    def test_plan_creation(self):
        """Test creating an execution plan"""
        plan = ExecutionPlan(plan_id="plan-001", goal="Test goal")
        self.assertEqual(plan.plan_id, "plan-001")
        self.assertEqual(plan.goal, "Test goal")
        self.assertEqual(plan.status, PlanStatus.DRAFT)
        self.assertEqual(len(plan.steps), 0)

    def test_plan_to_dict(self):
        """Test plan serialization"""
        plan = ExecutionPlan(plan_id="plan-002", goal="Serialize goal")
        data = plan.to_dict()
        self.assertEqual(data["plan_id"], "plan-002")
        self.assertEqual(data["status"], "draft")


class TestForwardThinkingEngine(unittest.TestCase):
    """Test cases for ForwardThinkingEngine"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = ForwardThinkingEngine(max_iterations=3)

    def test_create_plan(self):
        """Test creating a plan"""
        plan = self.engine.create_plan("Test goal")
        self.assertIsNotNone(plan)
        self.assertEqual(plan.goal, "Test goal")
        self.assertEqual(plan.status, PlanStatus.DRAFT)

    def test_create_plan_custom_id(self):
        """Test creating a plan with custom ID"""
        plan = self.engine.create_plan("Goal", plan_id="custom-plan")
        self.assertEqual(plan.plan_id, "custom-plan")

    def test_add_step(self):
        """Test adding steps to a plan"""
        plan = self.engine.create_plan("Goal")
        step = self.engine.add_step(
            plan_id=plan.plan_id,
            name="Step 1",
            description="First step",
        )
        self.assertIsNotNone(step)
        self.assertEqual(len(plan.steps), 1)

    def test_add_step_invalid_plan(self):
        """Test adding step to non-existent plan"""
        with self.assertRaises(ValueError):
            self.engine.add_step(
                plan_id="nonexistent",
                name="Step",
                description="Desc",
            )

    async def test_execute_plan_simple(self):
        """Test executing a simple plan"""
        results = []

        async def action1(**kwargs):
            results.append("step1")
            return "done1"

        async def action2(**kwargs):
            results.append("step2")
            return "done2"

        plan = self.engine.create_plan("Simple goal")
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Step 1",
            description="First",
            action=action1,
        )
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Step 2",
            description="Second",
            action=action2,
        )

        result = await self.engine.execute_plan(plan.plan_id)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(results), 2)

    async def test_execute_plan_with_dependencies(self):
        """Test executing a plan with step dependencies"""
        execution_order = []

        async def step1(**kwargs):
            execution_order.append("step1")
            return "result1"

        async def step2(**kwargs):
            execution_order.append("step2")
            return "result2"

        plan = self.engine.create_plan("Dep goal")
        s1 = self.engine.add_step(
            plan_id=plan.plan_id,
            name="Step 1",
            description="First",
            action=step1,
        )
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Step 2",
            description="Depends on Step 1",
            action=step2,
            depends_on=[s1.step_id],
        )

        result = await self.engine.execute_plan(plan.plan_id)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(execution_order, ["step1", "step2"])

    async def test_execute_plan_with_failure_and_retry(self):
        """Test plan execution with step failure and retry"""
        call_count = 0

        async def flaky_action(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Temporary failure")
            return "success"

        plan = self.engine.create_plan("Retry goal")
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Flaky Step",
            description="Fails first, succeeds second",
            action=flaky_action,
        )

        result = await self.engine.execute_plan(plan.plan_id)

        self.assertEqual(result["status"], "completed")
        self.assertGreater(call_count, 1)

    async def test_execute_plan_permanent_failure(self):
        """Test plan with permanently failing step"""
        async def always_fails(**kwargs):
            raise RuntimeError("Permanent failure")

        plan = self.engine.create_plan("Fail goal")
        step = self.engine.add_step(
            plan_id=plan.plan_id,
            name="Failing Step",
            description="Always fails",
            action=always_fails,
        )
        # Reduce retries for faster test
        plan.steps[0].max_retries = 1

        result = await self.engine.execute_plan(plan.plan_id)

        self.assertEqual(result["status"], "failed")

    async def test_execute_nonexistent_plan(self):
        """Test executing non-existent plan"""
        with self.assertRaises(ValueError):
            await self.engine.execute_plan("nonexistent")

    def test_get_plan(self):
        """Test getting a plan by ID"""
        plan = self.engine.create_plan("Lookup goal")
        retrieved = self.engine.get_plan(plan.plan_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.goal, "Lookup goal")

    def test_get_plan_nonexistent(self):
        """Test getting non-existent plan"""
        result = self.engine.get_plan("nonexistent")
        self.assertIsNone(result)

    async def test_execution_history(self):
        """Test execution history tracking"""
        plan = self.engine.create_plan("History goal")
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Step",
            description="Test",
        )

        await self.engine.execute_plan(plan.plan_id)

        history = self.engine.get_execution_history(plan.plan_id)
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]["plan_id"], plan.plan_id)

    def test_get_summary(self):
        """Test engine summary statistics"""
        self.engine.create_plan("Goal 1")
        self.engine.create_plan("Goal 2")

        summary = self.engine.get_summary()
        self.assertEqual(summary["total_plans"], 2)

    async def test_evaluation_handler(self):
        """Test evaluation handler registration and notification"""
        handler_called = False

        def on_eval(plan, evaluation):
            nonlocal handler_called
            handler_called = True

        self.engine.on_evaluation(on_eval)
        self.assertEqual(len(self.engine._evaluation_handlers), 1)

    async def test_no_action_step(self):
        """Test step with no action is auto-completed"""
        plan = self.engine.create_plan("No-action goal")
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Placeholder",
            description="No action defined",
        )

        result = await self.engine.execute_plan(plan.plan_id)
        self.assertEqual(result["status"], "completed")

    async def test_sync_action(self):
        """Test step with synchronous action"""
        def sync_action(**kwargs):
            return "sync_result"

        plan = self.engine.create_plan("Sync goal")
        self.engine.add_step(
            plan_id=plan.plan_id,
            name="Sync Step",
            description="Synchronous",
            action=sync_action,
        )

        result = await self.engine.execute_plan(plan.plan_id)
        self.assertEqual(result["status"], "completed")


# Apply async_test decorator to async test methods
TestForwardThinkingEngine.test_execute_plan_simple = async_test(
    TestForwardThinkingEngine.test_execute_plan_simple
)
TestForwardThinkingEngine.test_execute_plan_with_dependencies = async_test(
    TestForwardThinkingEngine.test_execute_plan_with_dependencies
)
TestForwardThinkingEngine.test_execute_plan_with_failure_and_retry = async_test(
    TestForwardThinkingEngine.test_execute_plan_with_failure_and_retry
)
TestForwardThinkingEngine.test_execute_plan_permanent_failure = async_test(
    TestForwardThinkingEngine.test_execute_plan_permanent_failure
)
TestForwardThinkingEngine.test_execute_nonexistent_plan = async_test(
    TestForwardThinkingEngine.test_execute_nonexistent_plan
)
TestForwardThinkingEngine.test_execution_history = async_test(
    TestForwardThinkingEngine.test_execution_history
)
TestForwardThinkingEngine.test_evaluation_handler = async_test(
    TestForwardThinkingEngine.test_evaluation_handler
)
TestForwardThinkingEngine.test_no_action_step = async_test(
    TestForwardThinkingEngine.test_no_action_step
)
TestForwardThinkingEngine.test_sync_action = async_test(
    TestForwardThinkingEngine.test_sync_action
)


if __name__ == "__main__":
    unittest.main()
