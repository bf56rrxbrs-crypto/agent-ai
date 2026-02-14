"""
Unit tests for the iOS Agent module.
"""

import unittest
import asyncio
import os
import tempfile

from ios_agent import IOSAgent, DeviceCapability, IOSDeviceProfile
from autonomous_agent import TaskPriority


def async_test(coro):
    """Decorator to run async tests"""
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper


class TestIOSDeviceProfile(unittest.TestCase):
    """Test cases for IOSDeviceProfile"""

    def test_default_profile(self):
        """Test default iPhone 17 Pro device profile"""
        profile = IOSDeviceProfile()
        self.assertEqual(profile.device_model, "iPhone 17 Pro")
        self.assertEqual(profile.os_version, "iOS 19")
        self.assertEqual(profile.chip, "A19 Pro")
        self.assertEqual(profile.ram_gb, 12)
        self.assertEqual(profile.neural_engine_cores, 18)
        self.assertTrue(profile.always_on_display)
        self.assertTrue(profile.dynamic_island)
        self.assertTrue(profile.apple_intelligence)
        self.assertTrue(profile.on_device_ai)
        self.assertTrue(profile.camera_control)
        self.assertTrue(profile.action_button)

    def test_profile_to_dict(self):
        """Test profile serialization"""
        profile = IOSDeviceProfile()
        data = profile.to_dict()
        self.assertIn("device_model", data)
        self.assertIn("supported_features", data)
        self.assertIsInstance(data["supported_features"], list)


class TestDeviceCapability(unittest.TestCase):
    """Test cases for DeviceCapability"""

    def test_capability_creation(self):
        """Test creating a device capability"""
        cap = DeviceCapability("test_cap", "Test capability")
        self.assertEqual(cap.name, "test_cap")
        self.assertTrue(cap.enabled)
        self.assertEqual(cap.usage_count, 0)

    async def test_capability_execution(self):
        """Test executing a capability"""
        cap = DeviceCapability("test_cap", "Test")
        result = await cap.execute(param1="value1")
        self.assertEqual(result["capability"], "test_cap")
        self.assertEqual(cap.usage_count, 1)

    async def test_capability_with_handler(self):
        """Test capability with custom handler"""
        async def handler(**kwargs):
            return {"handled": True}

        cap = DeviceCapability("custom", "Custom cap", handler=handler)
        result = await cap.execute()
        self.assertEqual(result["result"]["handled"], True)

    async def test_capability_with_sync_handler(self):
        """Test capability with synchronous handler"""
        def handler(**kwargs):
            return {"sync": True}

        cap = DeviceCapability("sync_cap", "Sync cap", handler=handler)
        result = await cap.execute()
        self.assertEqual(result["result"]["sync"], True)

    def test_capability_to_dict(self):
        """Test capability serialization"""
        cap = DeviceCapability("test", "Test cap")
        data = cap.to_dict()
        self.assertEqual(data["name"], "test")
        self.assertTrue(data["enabled"])


class TestIOSAgent(unittest.TestCase):
    """Test cases for IOSAgent"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, "test_memory.json")
        self.agent = IOSAgent(
            agent_id="test-ios-001",
            memory_path=self.memory_path,
        )

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_agent_initialization(self):
        """Test iOS agent initialization"""
        self.assertEqual(self.agent.agent_id, "test-ios-001")
        self.assertEqual(self.agent.device.device_model, "iPhone 17 Pro")
        self.assertGreater(len(self.agent.capabilities), 0)

    def test_default_capabilities(self):
        """Test default iOS capabilities are registered for iPhone 17 Pro"""
        expected_caps = [
            "notification_management",
            "shortcut_automation",
            "focus_mode_control",
            "app_management",
            "health_monitoring",
            "smart_scheduling",
            "communication_handler",
            "media_control",
            "device_optimization",
            "context_awareness",
            "apple_intelligence",
            "siri_integration",
            "camera_control",
            "action_button_config",
            "live_activities",
            "home_automation",
        ]
        for cap_name in expected_caps:
            self.assertIn(cap_name, self.agent.capabilities)

    def test_add_capability(self):
        """Test adding a custom capability"""
        cap = DeviceCapability("custom_cap", "Custom capability")
        self.agent.add_capability(cap)
        self.assertIn("custom_cap", self.agent.capabilities)

    def test_remember_and_recall(self):
        """Test memory remember and recall"""
        self.agent.remember("User prefers dark mode", importance=0.8)
        results = self.agent.recall("dark mode")
        self.assertEqual(len(results), 1)
        self.assertIn("dark mode", results[0]["content"])

    def test_reliability_initial(self):
        """Test initial reliability is 1.0"""
        self.assertEqual(self.agent.get_reliability(), 1.0)

    async def test_start_stop(self):
        """Test starting and stopping agent"""
        await self.agent.start()
        self.assertEqual(self.agent.agent.state.value, "active")

        await self.agent.stop()
        self.assertEqual(self.agent.agent.state.value, "shutdown")

    async def test_execute_instruction_with_planning(self):
        """Test executing instruction with forward-thinking planning"""
        await self.agent.start()

        result = await self.agent.execute_instruction(
            "Check my notifications",
            priority=TaskPriority.HIGH,
            use_planning=True,
        )

        self.assertIn("status", result)
        self.assertIn("instruction", result)
        self.assertEqual(result["instruction"], "Check my notifications")

        await self.agent.stop()

    async def test_execute_instruction_direct(self):
        """Test executing instruction without planning"""
        await self.agent.start()

        result = await self.agent.execute_instruction(
            "Set timer for 5 minutes",
            use_planning=False,
        )

        self.assertEqual(result["status"], "completed")

        await self.agent.stop()

    async def test_use_capability(self):
        """Test using a device capability"""
        result = await self.agent.use_capability("notification_management")
        self.assertEqual(result["capability"], "notification_management")

    async def test_use_invalid_capability(self):
        """Test using non-existent capability"""
        with self.assertRaises(ValueError):
            await self.agent.use_capability("nonexistent_cap")

    async def test_use_disabled_capability(self):
        """Test using disabled capability"""
        self.agent.capabilities["notification_management"].enabled = False
        with self.assertRaises(RuntimeError):
            await self.agent.use_capability("notification_management")

    def test_get_status(self):
        """Test comprehensive agent status"""
        status = self.agent.get_status()
        self.assertIn("agent_id", status)
        self.assertIn("device", status)
        self.assertIn("memory", status)
        self.assertIn("planning_engine", status)
        self.assertIn("capabilities", status)
        self.assertIn("reliability", status)

    async def test_reliability_tracking(self):
        """Test reliability tracking after instructions"""
        await self.agent.start()

        await self.agent.execute_instruction("Test 1", use_planning=False)
        await self.agent.execute_instruction("Test 2", use_planning=False)

        self.assertEqual(self.agent._instruction_count, 2)
        self.assertEqual(self.agent._successful_instructions, 2)
        self.assertEqual(self.agent.get_reliability(), 1.0)

        await self.agent.stop()

    async def test_memory_persistence_across_instructions(self):
        """Test that instructions are stored in memory"""
        await self.agent.start()

        await self.agent.execute_instruction("Remember this task", use_planning=False)

        results = self.agent.recall("Remember this task")
        self.assertGreater(len(results), 0)

        await self.agent.stop()

    async def test_execute_instruction_failure_returns_error_type(self):
        """Test that failed instructions include error_type in result"""
        await self.agent.start()

        # Monkey-patch _execute_core_action to force failure
        original = self.agent._execute_core_action

        async def failing_action(**kwargs):
            raise TypeError("simulated type error")

        self.agent._execute_core_action = failing_action

        result = await self.agent.execute_instruction(
            "Trigger failure", use_planning=False
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("error_type", result)
        self.assertEqual(result["error_type"], "TypeError")

        self.agent._execute_core_action = original
        await self.agent.stop()


# Apply async_test decorator to async test methods
TestDeviceCapability.test_capability_execution = async_test(
    TestDeviceCapability.test_capability_execution
)
TestDeviceCapability.test_capability_with_handler = async_test(
    TestDeviceCapability.test_capability_with_handler
)
TestDeviceCapability.test_capability_with_sync_handler = async_test(
    TestDeviceCapability.test_capability_with_sync_handler
)
TestIOSAgent.test_start_stop = async_test(TestIOSAgent.test_start_stop)
TestIOSAgent.test_execute_instruction_with_planning = async_test(
    TestIOSAgent.test_execute_instruction_with_planning
)
TestIOSAgent.test_execute_instruction_direct = async_test(
    TestIOSAgent.test_execute_instruction_direct
)
TestIOSAgent.test_use_capability = async_test(TestIOSAgent.test_use_capability)
TestIOSAgent.test_use_invalid_capability = async_test(
    TestIOSAgent.test_use_invalid_capability
)
TestIOSAgent.test_use_disabled_capability = async_test(
    TestIOSAgent.test_use_disabled_capability
)
TestIOSAgent.test_reliability_tracking = async_test(
    TestIOSAgent.test_reliability_tracking
)
TestIOSAgent.test_memory_persistence_across_instructions = async_test(
    TestIOSAgent.test_memory_persistence_across_instructions
)
TestIOSAgent.test_execute_instruction_failure_returns_error_type = async_test(
    TestIOSAgent.test_execute_instruction_failure_returns_error_type
)


if __name__ == "__main__":
    unittest.main()
