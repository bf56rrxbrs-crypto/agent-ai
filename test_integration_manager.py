"""
Unit tests for the Integration Manager module.
"""

import unittest
import asyncio

from integration_manager import (
    IntegrationManager,
    APIIntegration,
    WebhookIntegration,
    IntegrationConfig
)


class TestIntegrationManager(unittest.TestCase):
    """Test cases for IntegrationManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = IntegrationManager()
    
    async def test_register_integration(self):
        """Test registering an integration"""
        config = IntegrationConfig(
            integration_id="test-api",
            name="Test API",
            enabled=True,
            config={"base_url": "https://test.com"}
        )
        
        integration = APIIntegration(config)
        result = await self.manager.register_integration(integration)
        
        self.assertTrue(result)
        self.assertIn("test-api", self.manager.integrations)
    
    async def test_unregister_integration(self):
        """Test unregistering an integration"""
        config = IntegrationConfig(
            integration_id="test-api",
            name="Test API",
            enabled=True,
            config={"base_url": "https://test.com"}
        )
        
        integration = APIIntegration(config)
        await self.manager.register_integration(integration)
        
        result = await self.manager.unregister_integration("test-api")
        
        self.assertTrue(result)
        self.assertNotIn("test-api", self.manager.integrations)
    
    async def test_execute_integration(self):
        """Test executing an integration action"""
        config = IntegrationConfig(
            integration_id="test-api",
            name="Test API",
            enabled=True,
            config={"base_url": "https://test.com"}
        )
        
        integration = APIIntegration(config)
        await self.manager.register_integration(integration)
        
        result = await self.manager.execute_integration(
            "test-api",
            "test_action",
            {"param": "value"}
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
    
    async def test_health_check_all(self):
        """Test health check for all integrations"""
        config1 = IntegrationConfig(
            integration_id="test-api-1",
            name="Test API 1",
            enabled=True,
            config={"base_url": "https://test1.com"}
        )
        
        config2 = IntegrationConfig(
            integration_id="test-api-2",
            name="Test API 2",
            enabled=True,
            config={"base_url": "https://test2.com"}
        )
        
        await self.manager.register_integration(APIIntegration(config1))
        await self.manager.register_integration(APIIntegration(config2))
        
        results = await self.manager.health_check_all()
        
        self.assertEqual(len(results), 2)
        self.assertIn("test-api-1", results)
        self.assertIn("test-api-2", results)
    
    def test_list_integrations(self):
        """Test listing integrations"""
        integrations = self.manager.list_integrations()
        self.assertIsInstance(integrations, list)
    
    def test_get_stats(self):
        """Test getting integration statistics"""
        stats = self.manager.get_stats()
        
        self.assertIn("total_integrations", stats)
        self.assertIn("active_integrations", stats)
        self.assertIn("stats", stats)


class TestAPIIntegration(unittest.TestCase):
    """Test cases for APIIntegration"""
    
    async def test_connect(self):
        """Test API connection"""
        config = IntegrationConfig(
            integration_id="test-api",
            name="Test API",
            enabled=True,
            config={
                "base_url": "https://api.test.com",
                "api_key": "test-key"
            }
        )
        
        integration = APIIntegration(config)
        result = await integration.connect()
        
        self.assertTrue(result)
        self.assertTrue(integration.is_connected)
    
    async def test_disconnect(self):
        """Test API disconnection"""
        config = IntegrationConfig(
            integration_id="test-api",
            name="Test API",
            enabled=True,
            config={"base_url": "https://api.test.com"}
        )
        
        integration = APIIntegration(config)
        await integration.connect()
        result = await integration.disconnect()
        
        self.assertTrue(result)
        self.assertFalse(integration.is_connected)
    
    async def test_health_check(self):
        """Test API health check"""
        config = IntegrationConfig(
            integration_id="test-api",
            name="Test API",
            enabled=True,
            config={"base_url": "https://api.test.com"}
        )
        
        integration = APIIntegration(config)
        await integration.connect()
        
        is_healthy = await integration.health_check()
        self.assertTrue(is_healthy)


def async_test(coro):
    """Decorator to run async tests"""
    def wrapper(*args, **kwargs):
        return asyncio.run(coro(*args, **kwargs))
    return wrapper


# Apply decorator to async test methods
TestIntegrationManager.test_register_integration = async_test(
    TestIntegrationManager.test_register_integration
)
TestIntegrationManager.test_unregister_integration = async_test(
    TestIntegrationManager.test_unregister_integration
)
TestIntegrationManager.test_execute_integration = async_test(
    TestIntegrationManager.test_execute_integration
)
TestIntegrationManager.test_health_check_all = async_test(
    TestIntegrationManager.test_health_check_all
)

TestAPIIntegration.test_connect = async_test(TestAPIIntegration.test_connect)
TestAPIIntegration.test_disconnect = async_test(TestAPIIntegration.test_disconnect)
TestAPIIntegration.test_health_check = async_test(TestAPIIntegration.test_health_check)


if __name__ == "__main__":
    unittest.main()
