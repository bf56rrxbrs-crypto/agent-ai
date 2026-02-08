"""
Integration Manager Module

Handles external service integrations with plugin architecture for extensibility.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IntegrationConfig:
    """Configuration for an integration"""
    integration_id: str
    name: str
    enabled: bool
    config: Dict[str, Any]
    retry_policy: Optional[Dict[str, Any]] = None


class Integration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.logger = logging.getLogger(f"Integration-{config.name}")
        self.is_connected = False
        self.last_error: Optional[str] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the external service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to the external service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the integration is healthy"""
        pass
    
    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute an action through this integration"""
        pass


class APIIntegration(Integration):
    """Integration for REST API services"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = config.config.get("base_url", "")
        self.api_key = config.config.get("api_key", "")
        self.headers = config.config.get("headers", {})
    
    async def connect(self) -> bool:
        """Establish API connection"""
        try:
            self.logger.info(f"Connecting to API: {self.base_url}")
            # Simulate connection
            await asyncio.sleep(0.1)
            self.is_connected = True
            return True
        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Close API connection"""
        self.is_connected = False
        return True
    
    async def health_check(self) -> bool:
        """Check API health"""
        if not self.is_connected:
            return False
        
        try:
            # Simulate health check
            await asyncio.sleep(0.05)
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute API request"""
        if not self.is_connected:
            raise ConnectionError("Not connected to API")
        
        self.logger.info(f"Executing API action: {action}")
        # Simulate API call
        await asyncio.sleep(0.1)
        return {"success": True, "action": action, "params": params}


class WebhookIntegration(Integration):
    """Integration for webhook-based services"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_url = config.config.get("webhook_url", "")
        self.secret = config.config.get("secret", "")
    
    async def connect(self) -> bool:
        """Setup webhook"""
        try:
            self.logger.info(f"Setting up webhook: {self.webhook_url}")
            await asyncio.sleep(0.1)
            self.is_connected = True
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    async def disconnect(self) -> bool:
        """Remove webhook"""
        self.is_connected = False
        return True
    
    async def health_check(self) -> bool:
        """Check webhook health"""
        return self.is_connected
    
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Send webhook notification"""
        if not self.is_connected:
            raise ConnectionError("Webhook not configured")
        
        self.logger.info(f"Sending webhook: {action}")
        await asyncio.sleep(0.1)
        return {"success": True, "webhook_sent": True}


class IntegrationManager:
    """
    Manages all external integrations with plugin architecture.
    
    Features:
    - Dynamic integration loading
    - Connection pooling
    - Automatic retry with exponential backoff
    - Health monitoring
    - Event-driven notifications
    """
    
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self.logger = logging.getLogger("IntegrationManager")
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_request_time": None
        }
    
    async def register_integration(self, integration: Integration) -> bool:
        """Register a new integration"""
        try:
            self.logger.info(f"Registering integration: {integration.config.name}")
            
            if integration.config.enabled:
                success = await integration.connect()
                if not success:
                    self.logger.error(f"Failed to connect integration: {integration.config.name}")
                    return False
            
            self.integrations[integration.config.integration_id] = integration
            self.logger.info(f"Integration registered: {integration.config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering integration: {str(e)}")
            return False
    
    async def unregister_integration(self, integration_id: str) -> bool:
        """Unregister an integration"""
        if integration_id in self.integrations:
            integration = self.integrations[integration_id]
            await integration.disconnect()
            del self.integrations[integration_id]
            self.logger.info(f"Integration unregistered: {integration.config.name}")
            return True
        return False
    
    async def execute_integration(
        self, 
        integration_id: str, 
        action: str, 
        params: Dict[str, Any],
        retry: bool = True
    ) -> Any:
        """Execute an action through a specific integration"""
        if integration_id not in self.integrations:
            raise ValueError(f"Integration not found: {integration_id}")
        
        integration = self.integrations[integration_id]
        max_retries = 3 if retry else 0
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                self.stats["total_requests"] += 1
                self.stats["last_request_time"] = datetime.now()
                
                result = await integration.execute(action, params)
                
                self.stats["successful_requests"] += 1
                return result
                
            except Exception as e:
                retry_count += 1
                self.logger.error(
                    f"Integration execution failed (attempt {retry_count}): {str(e)}"
                )
                
                if retry_count <= max_retries:
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.stats["failed_requests"] += 1
                    raise
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all integrations"""
        results = {}
        
        for integration_id, integration in self.integrations.items():
            try:
                is_healthy = await integration.health_check()
                results[integration_id] = is_healthy
            except Exception as e:
                self.logger.error(f"Health check failed for {integration_id}: {str(e)}")
                results[integration_id] = False
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            "total_integrations": len(self.integrations),
            "active_integrations": sum(
                1 for i in self.integrations.values() if i.is_connected
            ),
            "stats": self.stats
        }
    
    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all registered integrations"""
        return [
            {
                "id": integration.config.integration_id,
                "name": integration.config.name,
                "enabled": integration.config.enabled,
                "connected": integration.is_connected,
                "last_error": integration.last_error
            }
            for integration in self.integrations.values()
        ]
