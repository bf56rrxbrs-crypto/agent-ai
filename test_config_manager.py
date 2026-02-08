"""
Unit tests for the Configuration Manager module.
"""

import unittest
import os
import json
from config_manager import ConfigManager, AgentConfig, CacheConfig


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_manager = ConfigManager()
        self.test_config_file = "/tmp/test_config.json"
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
    
    def test_initialization(self):
        """Test config manager initialization"""
        self.assertIsNotNone(self.config_manager.config)
        self.assertIn("agent", self.config_manager.config)
    
    def test_get_value(self):
        """Test getting configuration values"""
        value = self.config_manager.get("agent.agent_id")
        self.assertIsNotNone(value)
    
    def test_set_value(self):
        """Test setting configuration values"""
        result = self.config_manager.set("agent.custom_field", "test_value")
        self.assertTrue(result)
        
        value = self.config_manager.get("agent.custom_field")
        self.assertEqual(value, "test_value")
    
    def test_get_with_default(self):
        """Test getting non-existent value with default"""
        value = self.config_manager.get("nonexistent.key", "default_value")
        self.assertEqual(value, "default_value")
    
    def test_validate_valid_config(self):
        """Test validating valid configuration"""
        self.config_manager.set("agent.agent_id", "test-agent")
        self.config_manager.set("agent.name", "Test Agent")
        self.config_manager.set("agent.max_concurrent_tasks", 5)
        self.config_manager.set("agent.task_timeout", 300)
        
        is_valid, error = self.config_manager.validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_invalid_config(self):
        """Test validating invalid configuration"""
        self.config_manager.set("agent.agent_id", "")
        
        is_valid, error = self.config_manager.validate()
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        self.config_manager.set("agent.test_field", "test_value")
        
        # Save
        result = self.config_manager.save_config(self.test_config_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_config_file))
        
        # Load in new instance
        new_manager = ConfigManager(self.test_config_file)
        value = new_manager.get("agent.test_field")
        self.assertEqual(value, "test_value")
    
    def test_get_agent_config(self):
        """Test getting typed agent configuration"""
        config = self.config_manager.get_agent_config()
        
        self.assertIsInstance(config, AgentConfig)
        self.assertIsNotNone(config.agent_id)
        self.assertIsNotNone(config.name)
    
    def test_get_cache_config(self):
        """Test getting typed cache configuration"""
        config = self.config_manager.get_cache_config()
        
        self.assertIsInstance(config, CacheConfig)
        self.assertTrue(config.enabled)
    
    def test_to_dict(self):
        """Test exporting configuration as dictionary"""
        config_dict = self.config_manager.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn("agent", config_dict)
        self.assertIn("cache", config_dict)


if __name__ == "__main__":
    unittest.main()
