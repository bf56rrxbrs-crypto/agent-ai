"""
Configuration Management Module

Handles configuration loading, validation, and management for the autonomous agent.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AgentConfig:
    """Main agent configuration"""
    agent_id: str
    name: str
    log_level: str = "INFO"
    max_concurrent_tasks: int = 5
    health_check_interval: int = 30
    task_timeout: int = 300
    enable_auto_recovery: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    max_size: int = 1000
    ttl_seconds: int = 3600
    strategy: str = "lru"  # lru, lfu, or fifo


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    metrics_interval: int = 60
    log_rotation: bool = True
    max_log_size_mb: int = 100


class ConfigManager:
    """
    Manages configuration with support for multiple environments and hot-reloading.
    
    Features:
    - Environment-specific configurations
    - Configuration validation
    - Hot-reloading support
    - Default fallbacks
    """
    
    DEFAULT_CONFIG = {
        "agent": {
            "agent_id": "default-agent",
            "name": "Autonomous AI Agent",
            "log_level": "INFO",
            "max_concurrent_tasks": 5,
            "health_check_interval": 30,
            "task_timeout": 300,
            "enable_auto_recovery": True
        },
        "cache": {
            "enabled": True,
            "max_size": 1000,
            "ttl_seconds": 3600,
            "strategy": "lru"
        },
        "monitoring": {
            "enabled": True,
            "metrics_interval": 60,
            "log_rotation": True,
            "max_log_size_mb": 100
        },
        "integrations": {
            "enabled": [],
            "configs": {}
        }
    }
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "production"):
        self.config_path = config_path
        self.environment = environment
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> bool:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults
            self._deep_merge(self.config, loaded_config)
            return True
            
        except Exception as e:
            print(f"Error loading config from {config_path}: {str(e)}")
            return False
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save current configuration to file"""
        path = config_path or self.config_path
        if not path:
            return False
        
        try:
            # Create directory if it doesn't exist
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
            
        except Exception as e:
            print(f"Error saving config to {path}: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return True
    
    def get_agent_config(self) -> AgentConfig:
        """Get typed agent configuration"""
        agent_dict = self.config.get("agent", {})
        return AgentConfig(**agent_dict)
    
    def get_cache_config(self) -> CacheConfig:
        """Get typed cache configuration"""
        cache_dict = self.config.get("cache", {})
        return CacheConfig(**cache_dict)
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get typed monitoring configuration"""
        monitoring_dict = self.config.get("monitoring", {})
        return MonitoringConfig(**monitoring_dict)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate configuration"""
        # Check required fields
        if not self.get("agent.agent_id"):
            return False, "agent.agent_id is required"
        
        if not self.get("agent.name"):
            return False, "agent.name is required"
        
        # Validate numeric ranges
        max_tasks = self.get("agent.max_concurrent_tasks", 0)
        if max_tasks <= 0:
            return False, "agent.max_concurrent_tasks must be positive"
        
        timeout = self.get("agent.task_timeout", 0)
        if timeout <= 0:
            return False, "agent.task_timeout must be positive"
        
        # Validate cache config
        if self.get("cache.enabled"):
            max_size = self.get("cache.max_size", 0)
            if max_size <= 0:
                return False, "cache.max_size must be positive when cache is enabled"
        
        return True, None
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def reload(self) -> bool:
        """Reload configuration from file"""
        if self.config_path and os.path.exists(self.config_path):
            return self.load_config(self.config_path)
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self.config.copy()
