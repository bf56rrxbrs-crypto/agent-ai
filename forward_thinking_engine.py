"""
Forward-Thinking Structural Loop Engine

Implements anticipatory planning with plan-execute-evaluate cycles for
the autonomous AI agent. Enables multi-step reasoning, goal decomposition,
and adaptive re-planning based on execution outcomes.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class StepStatus(Enum):
    """Status of a plan step"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStatus(Enum):
    """Status of an execution plan"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLANNING = "replanning"


@dataclass
class PlanStep:
    """Represents a single step in an execution plan"""
    step_id: str
    name: str
    description: str
    action: Optional[Callable] = None
    params: Dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding non-serializable action)"""
        data = {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "params": self.params,
            "status": self.status.value,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "depends_on": self.depends_on,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }
        return data


@dataclass
class ExecutionPlan:
    """Represents a complete execution plan with ordered steps"""
    plan_id: str
    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: str = ""
    completed_at: Optional[str] = None
    iteration: int = 0
    max_iterations: int = 5

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
        }


class ForwardThinkingEngine:
    """
    Forward-thinking structural loop engine for anticipatory planning.

    Implements a plan-execute-evaluate cycle:
    1. PLAN: Decompose goals into ordered steps with dependencies
    2. EXECUTE: Run steps respecting dependency order
    3. EVALUATE: Assess outcomes and adapt the plan
    4. LOOP: Re-plan if needed based on evaluation

    Features:
    - Goal decomposition into actionable steps
    - Dependency-aware step execution
    - Outcome evaluation with adaptive re-planning
    - Execution history for learning
    - Configurable iteration limits
    """

    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self.plans: Dict[str, ExecutionPlan] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("ForwardThinkingEngine")
        self._plan_counter = 0
        self._evaluation_handlers: List[Callable] = []

    def create_plan(
        self,
        goal: str,
        steps: Optional[List[PlanStep]] = None,
        plan_id: Optional[str] = None,
    ) -> ExecutionPlan:
        """
        Create a new execution plan for a goal.

        Args:
            goal: The high-level goal to achieve
            steps: Optional pre-defined steps
            plan_id: Optional custom plan ID

        Returns:
            The created ExecutionPlan
        """
        self._plan_counter += 1
        pid = plan_id or f"plan-{self._plan_counter:04d}"

        plan = ExecutionPlan(
            plan_id=pid,
            goal=goal,
            steps=steps or [],
            max_iterations=self.max_iterations,
        )

        self.plans[pid] = plan
        self.logger.info(f"Plan created: {pid} - Goal: {goal}")
        return plan

    def add_step(
        self,
        plan_id: str,
        name: str,
        description: str,
        action: Optional[Callable] = None,
        params: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None,
        step_id: Optional[str] = None,
    ) -> PlanStep:
        """
        Add a step to an existing plan.

        Args:
            plan_id: The plan to add the step to
            name: Step name
            description: Step description
            action: Callable to execute for this step
            params: Parameters for the action
            depends_on: List of step IDs this step depends on
            step_id: Optional custom step ID

        Returns:
            The created PlanStep
        """
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")

        plan = self.plans[plan_id]
        sid = step_id or f"{plan_id}-step-{len(plan.steps) + 1:03d}"

        step = PlanStep(
            step_id=sid,
            name=name,
            description=description,
            action=action,
            params=params or {},
            depends_on=depends_on or [],
        )

        plan.steps.append(step)
        self.logger.info(f"Step added to {plan_id}: {sid} - {name}")
        return step

    async def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a plan using the forward-thinking loop.

        The loop:
        1. Execute ready steps (dependencies satisfied)
        2. Evaluate outcomes
        3. Re-plan if needed
        4. Repeat until complete or max iterations reached

        Args:
            plan_id: The plan to execute

        Returns:
            Execution result summary
        """
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")

        plan = self.plans[plan_id]
        plan.status = PlanStatus.ACTIVE

        self.logger.info(f"Executing plan: {plan_id} - {plan.goal}")

        while plan.iteration < plan.max_iterations:
            plan.iteration += 1
            self.logger.info(
                f"Plan {plan_id} - Iteration {plan.iteration}/{plan.max_iterations}"
            )

            # Phase 1: Execute ready steps
            executed = await self._execute_ready_steps(plan)

            # Phase 2: Evaluate outcomes
            evaluation = self._evaluate_plan(plan)

            # Record history
            self.execution_history.append({
                "plan_id": plan_id,
                "iteration": plan.iteration,
                "steps_executed": executed,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat(),
            })

            # Phase 3: Check completion
            if evaluation["all_completed"]:
                plan.status = PlanStatus.COMPLETED
                plan.completed_at = datetime.now().isoformat()
                self.logger.info(f"Plan {plan_id} completed successfully")
                break

            if evaluation["has_failures"] and not evaluation["can_continue"]:
                plan.status = PlanStatus.FAILED
                self.logger.error(f"Plan {plan_id} failed - unrecoverable errors")
                break

            # Phase 4: Re-plan if needed (notify evaluation handlers)
            if evaluation["needs_replanning"]:
                plan.status = PlanStatus.REPLANNING
                await self._notify_evaluation_handlers(plan, evaluation)
                plan.status = PlanStatus.ACTIVE

        if plan.status == PlanStatus.ACTIVE:
            # Max iterations reached without completion
            plan.status = PlanStatus.FAILED
            self.logger.warning(
                f"Plan {plan_id} reached max iterations without completion"
            )

        return self._get_plan_result(plan)

    async def _execute_ready_steps(self, plan: ExecutionPlan) -> int:
        """Execute all steps whose dependencies are satisfied"""
        executed = 0

        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue

            # Check dependencies
            if not self._dependencies_satisfied(plan, step):
                continue

            # Execute step
            await self._execute_step(step)
            executed += 1

        return executed

    def _dependencies_satisfied(self, plan: ExecutionPlan, step: PlanStep) -> bool:
        """Check if all dependencies for a step are satisfied"""
        if not step.depends_on:
            return True

        step_map = {s.step_id: s for s in plan.steps}

        for dep_id in step.depends_on:
            if dep_id not in step_map:
                return False
            if step_map[dep_id].status != StepStatus.COMPLETED:
                return False

        return True

    async def _execute_step(self, step: PlanStep):
        """Execute a single plan step"""
        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.now().isoformat()

        try:
            self.logger.info(f"Executing step: {step.step_id} - {step.name}")

            if step.action is not None:
                if asyncio.iscoroutinefunction(step.action):
                    step.result = await step.action(**step.params)
                else:
                    step.result = step.action(**step.params)
            else:
                # No action defined - mark as completed (placeholder step)
                step.result = {"status": "no_action", "description": step.description}

            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now().isoformat()
            self.logger.info(f"Step {step.step_id} completed")

        except Exception as e:
            step.error = str(e)
            step.retry_count += 1

            if step.retry_count <= step.max_retries:
                # Reset to pending for retry
                step.status = StepStatus.PENDING
                self.logger.warning(
                    f"Step {step.step_id} failed (attempt {step.retry_count}), "
                    f"will retry: {e}"
                )
            else:
                step.status = StepStatus.FAILED
                step.completed_at = datetime.now().isoformat()
                self.logger.error(
                    f"Step {step.step_id} failed permanently: {e}"
                )

    def _evaluate_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Evaluate the current state of plan execution"""
        total = len(plan.steps)
        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        failed = sum(1 for s in plan.steps if s.status == StepStatus.FAILED)
        pending = sum(1 for s in plan.steps if s.status == StepStatus.PENDING)

        all_completed = completed == total and total > 0
        has_failures = failed > 0
        # Can continue if there are still pending steps
        can_continue = pending > 0
        # Needs replanning if there are failures but also pending steps
        needs_replanning = has_failures and can_continue

        return {
            "total_steps": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "progress": completed / total if total > 0 else 0.0,
            "all_completed": all_completed,
            "has_failures": has_failures,
            "can_continue": can_continue,
            "needs_replanning": needs_replanning,
        }

    def on_evaluation(self, handler: Callable):
        """Register an evaluation handler for re-planning notifications"""
        self._evaluation_handlers.append(handler)

    async def _notify_evaluation_handlers(
        self, plan: ExecutionPlan, evaluation: Dict[str, Any]
    ):
        """Notify evaluation handlers for potential re-planning"""
        for handler in self._evaluation_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(plan, evaluation)
                else:
                    handler(plan, evaluation)
            except Exception as e:
                self.logger.error(f"Error in evaluation handler: {e}")

    def _get_plan_result(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Get the final result of a plan execution"""
        evaluation = self._evaluate_plan(plan)
        return {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "status": plan.status.value,
            "iterations": plan.iteration,
            "evaluation": evaluation,
            "steps": [s.to_dict() for s in plan.steps],
        }

    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """Get a plan by ID"""
        return self.plans.get(plan_id)

    def get_execution_history(self, plan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get execution history, optionally filtered by plan ID.

        Args:
            plan_id: Optional plan ID to filter by

        Returns:
            List of history entries
        """
        if plan_id:
            return [h for h in self.execution_history if h["plan_id"] == plan_id]
        return list(self.execution_history)

    def get_summary(self) -> Dict[str, Any]:
        """Get engine summary statistics"""
        total_plans = len(self.plans)
        completed = sum(
            1 for p in self.plans.values() if p.status == PlanStatus.COMPLETED
        )
        failed = sum(
            1 for p in self.plans.values() if p.status == PlanStatus.FAILED
        )
        active = sum(
            1 for p in self.plans.values() if p.status == PlanStatus.ACTIVE
        )

        return {
            "total_plans": total_plans,
            "completed_plans": completed,
            "failed_plans": failed,
            "active_plans": active,
            "total_history_entries": len(self.execution_history),
        }
