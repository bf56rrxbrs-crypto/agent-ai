"""
Main entry point for the Autonomous AI Agent.

This module demonstrates the usage of all autonomous features and integrations,
including the iOS Agent with forward-thinking structural loop engineering
and persistent memory.
"""

import asyncio
import logging
from datetime import datetime

from autonomous_agent import AutonomousAgent, Task, TaskPriority
from integration_manager import (
    IntegrationManager, 
    APIIntegration, 
    WebhookIntegration,
    IntegrationConfig
)
from config_manager import ConfigManager
from cache_manager import CacheManager
from ios_agent import IOSAgent
from persistent_memory import PersistentMemory
from forward_thinking_engine import ForwardThinkingEngine


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def sample_task_action(**kwargs):
    """Sample task action"""
    task_name = kwargs.get('task_name', 'unknown')
    duration = kwargs.get('duration', 1)
    
    print(f"Executing task: {task_name}")
    await asyncio.sleep(duration)
    print(f"Task {task_name} completed")
    
    return {"status": "success", "task": task_name}


async def main():
    """Main execution function demonstrating autonomous features"""
    
    print("=" * 60)
    print("Autonomous AI Agent - Demo")
    print("=" * 60)
    
    # 1. Initialize Configuration Manager
    print("\n1. Initializing Configuration Manager...")
    config_manager = ConfigManager()
    config_manager.set("agent.agent_id", "demo-agent-001")
    config_manager.set("agent.name", "Demo Autonomous Agent")
    
    is_valid, error = config_manager.validate()
    if is_valid:
        print("✓ Configuration validated successfully")
    else:
        print(f"✗ Configuration validation failed: {error}")
        return
    
    # 2. Initialize Cache Manager
    print("\n2. Initializing Cache Manager...")
    cache = CacheManager(strategy="lru", max_size=100, default_ttl=3600)
    cache.set("demo_key", "demo_value")
    cached_value = cache.get("demo_key")
    print(f"✓ Cache test: {cached_value}")
    print(f"  Cache stats: {cache.get_stats()}")
    
    # 3. Initialize Integration Manager
    print("\n3. Initializing Integration Manager...")
    integration_manager = IntegrationManager()
    
    # Register API integration
    api_config = IntegrationConfig(
        integration_id="api-001",
        name="Demo API",
        enabled=True,
        config={
            "base_url": "https://api.example.com",
            "api_key": "demo-key-123"
        }
    )
    api_integration = APIIntegration(api_config)
    await integration_manager.register_integration(api_integration)
    
    # Register Webhook integration
    webhook_config = IntegrationConfig(
        integration_id="webhook-001",
        name="Demo Webhook",
        enabled=True,
        config={
            "webhook_url": "https://hooks.example.com/webhook",
            "secret": "demo-secret"
        }
    )
    webhook_integration = WebhookIntegration(webhook_config)
    await integration_manager.register_integration(webhook_integration)
    
    print(f"✓ Registered {len(integration_manager.integrations)} integrations")
    print(f"  Integrations: {[i['name'] for i in integration_manager.list_integrations()]}")
    
    # 4. Initialize Autonomous Agent
    print("\n4. Initializing Autonomous Agent...")
    agent_config = config_manager.get_agent_config()
    agent = AutonomousAgent(
        agent_id=agent_config.agent_id,
        config=agent_config.to_dict()
    )
    
    # Register event handlers
    def on_task_completed(data):
        print(f"  [Event] Task completed: {data['task_id']}")
    
    def on_task_failed(data):
        print(f"  [Event] Task failed: {data['task_id']} - {data['error']}")
    
    agent.on("task_completed", on_task_completed)
    agent.on("task_failed", on_task_failed)
    
    # Start the agent
    await agent.start()
    print("✓ Agent started successfully")
    
    # 5. Add autonomous tasks
    print("\n5. Adding autonomous tasks to queue...")
    
    tasks = [
        Task(
            task_id="task-001",
            name="High Priority Task",
            priority=TaskPriority.HIGH,
            action=sample_task_action,
            params={"task_name": "Data Processing", "duration": 0.5},
            created_at=datetime.now()
        ),
        Task(
            task_id="task-002",
            name="Medium Priority Task",
            priority=TaskPriority.MEDIUM,
            action=sample_task_action,
            params={"task_name": "Report Generation", "duration": 0.3},
            created_at=datetime.now()
        ),
        Task(
            task_id="task-003",
            name="Low Priority Task",
            priority=TaskPriority.LOW,
            action=sample_task_action,
            params={"task_name": "Cleanup", "duration": 0.2},
            created_at=datetime.now()
        )
    ]
    
    for task in tasks:
        agent.add_task(task)
    
    print(f"✓ Added {len(tasks)} tasks to queue")
    
    # 6. Execute integrations
    print("\n6. Testing integrations...")
    
    try:
        # Execute API integration
        api_result = await integration_manager.execute_integration(
            "api-001",
            "fetch_data",
            {"endpoint": "/users", "limit": 10}
        )
        print(f"✓ API integration executed: {api_result}")
        
        # Execute Webhook integration
        webhook_result = await integration_manager.execute_integration(
            "webhook-001",
            "notify",
            {"event": "task_completed", "data": {"task_id": "task-001"}}
        )
        print(f"✓ Webhook integration executed: {webhook_result}")
        
    except Exception as e:
        print(f"✗ Integration error: {str(e)}")
    
    # 7. Monitor agent status
    print("\n7. Monitoring agent status...")
    
    # Wait for tasks to complete
    await asyncio.sleep(3)
    
    status = agent.get_status()
    print(f"✓ Agent Status:")
    print(f"  - State: {status['state']}")
    print(f"  - Health: {status['health']['is_healthy']}")
    print(f"  - Uptime: {status['health']['uptime_seconds']:.2f}s")
    print(f"  - Queue Size: {status['queue_size']}")
    print(f"  - Completed Tasks: {status['completed_tasks']}")
    print(f"  - Failed Tasks: {status['failed_tasks']}")
    
    # 8. Check integration health
    print("\n8. Checking integration health...")
    health_results = await integration_manager.health_check_all()
    for integration_id, is_healthy in health_results.items():
        status_icon = "✓" if is_healthy else "✗"
        print(f"  {status_icon} {integration_id}: {'Healthy' if is_healthy else 'Unhealthy'}")
    
    # 9. Display statistics
    print("\n9. Statistics:")
    integration_stats = integration_manager.get_stats()
    print(f"  Integration Stats:")
    print(f"    - Total Integrations: {integration_stats['total_integrations']}")
    print(f"    - Active Integrations: {integration_stats['active_integrations']}")
    print(f"    - Total Requests: {integration_stats['stats']['total_requests']}")
    print(f"    - Successful Requests: {integration_stats['stats']['successful_requests']}")
    
    cache_stats = cache.get_stats()
    print(f"  Cache Stats:")
    print(f"    - Strategy: {cache_stats['strategy']}")
    print(f"    - Size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"    - Hit Rate: {cache_stats['hit_rate']:.2%}")
    
    # 10. Graceful shutdown
    print("\n10. Shutting down agent...")
    await agent.stop()
    print("✓ Agent stopped gracefully")
    
    # ================================================================
    # 11. iOS Agent Demo - iPhone 17 Pro
    # ================================================================
    print("\n" + "=" * 60)
    print("iOS Agent Assistant - iPhone 17 Pro Demo")
    print("=" * 60)
    
    # Initialize iOS Agent
    print("\n11. Initializing iOS Agent for iPhone 17 Pro...")
    ios_agent = IOSAgent(
        agent_id="iphone17pro-agent",
        memory_path="/tmp/ios_agent_demo_memory.json",
    )
    await ios_agent.start()
    
    device = ios_agent.device
    print(f"✓ iOS Agent started on {device.device_model}")
    print(f"  - OS: {device.os_version}")
    print(f"  - Chip: {device.chip} ({device.gpu_cores}-core GPU)")
    print(f"  - Neural Engine: {device.neural_engine_cores} cores")
    print(f"  - Apple Intelligence: {'Enabled' if device.apple_intelligence else 'Disabled'}")
    print(f"  - On-Device AI: {'Enabled' if device.on_device_ai else 'Disabled'}")
    print(f"  - ProMotion 120Hz: {'Yes' if device.promotion_display else 'No'}")
    print(f"  - Capabilities: {len(ios_agent.capabilities)}")
    print(f"  - Supported Features: {len(device.supported_features)}")
    
    # 12. Persistent Memory Demo
    print("\n12. Persistent Memory...")
    ios_agent.remember("User prefers dark mode", importance=0.9)
    ios_agent.remember("Morning routine: news, weather, calendar", category="user_context", importance=0.8)
    ios_agent.remember("Preferred language: English", importance=0.7)
    
    recall_results = ios_agent.recall("dark mode")
    print(f"✓ Stored 3 memories, recalled: {recall_results[0]['content']}")
    
    memory_summary = ios_agent.memory.get_summary()
    print(f"  - Total memories: {memory_summary['total_memories']}")
    print(f"  - Categories: {list(memory_summary['categories'].keys())}")
    
    # 13. Forward-Thinking Planning Demo
    print("\n13. Forward-Thinking Structural Loop Engineering...")
    
    result = await ios_agent.execute_instruction(
        "Check notifications and prioritize important messages",
        priority=TaskPriority.HIGH,
        use_planning=True,
    )
    print(f"✓ Planned instruction: status={result['status']}")
    print(f"  - Plan iterations: {result.get('iterations', 'N/A')}")
    
    result2 = await ios_agent.execute_instruction(
        "Optimize battery settings for travel mode",
        priority=TaskPriority.MEDIUM,
        use_planning=True,
    )
    print(f"✓ Planned instruction: status={result2['status']}")
    
    # 14. Device Capabilities Demo
    print("\n14. iOS Device Capabilities (iPhone 17 Pro)...")
    
    cap_result = await ios_agent.use_capability("notification_management")
    print(f"✓ Notification management: {cap_result['capability']}")
    
    cap_result2 = await ios_agent.use_capability("focus_mode_control")
    print(f"✓ Focus mode control: {cap_result2['capability']}")
    
    cap_result3 = await ios_agent.use_capability("device_optimization")
    print(f"✓ Device optimization: {cap_result3['capability']}")
    
    cap_result4 = await ios_agent.use_capability("apple_intelligence")
    print(f"✓ Apple Intelligence: {cap_result4['capability']}")
    
    cap_result5 = await ios_agent.use_capability("camera_control")
    print(f"✓ Camera Control: {cap_result5['capability']}")
    
    cap_result6 = await ios_agent.use_capability("action_button_config")
    print(f"✓ Action Button: {cap_result6['capability']}")
    
    # 15. iOS Agent Status
    print("\n15. iOS Agent Status:")
    ios_status = ios_agent.get_status()
    print(f"  - Device: {ios_status['device']['device_model']}")
    print(f"  - Reliability: {ios_status['reliability']['rate']:.1%}")
    print(f"  - Instructions handled: {ios_status['reliability']['total_instructions']}")
    print(f"  - Memory entries: {ios_status['memory']['total_memories']}")
    print(f"  - Plans created: {ios_status['planning_engine']['total_plans']}")
    
    # 16. Graceful shutdown
    print("\n16. Shutting down iOS Agent...")
    await ios_agent.stop()
    print("✓ iOS Agent stopped gracefully")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        logging.exception("Fatal error in main")
