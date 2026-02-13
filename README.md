# Agent-AI: Autonomous AI Agent Framework

A comprehensive autonomous AI agent framework with robust integration capabilities, intelligent task management, and self-monitoring features. Includes an **iOS Agent assistant tailored for iPhone 17 Pro** with forward-thinking structural loop engineering and persistent memory. Designed to be reliable, efficient, and highly extensible.

## 🚀 Features

### iOS Agent Assistant (iPhone 17 Pro)
- **Forward-Thinking Structural Loop Engineering**: Plan-execute-evaluate cycles with adaptive re-planning for anticipatory multi-step reasoning
- **Persistent Memory**: Cross-session JSON-backed memory with categorized recall, importance scoring, and automatic cleanup
- **iOS Device Capabilities**: Tailored for iPhone 17 Pro with notification management, Focus modes, Shortcuts automation, health monitoring, and more
- **Reliability Tracking**: Instruction-level success tracking for consistent, dependable execution

### Autonomous Capabilities
- **Self-Monitoring**: Continuous health checks and status monitoring
- **Autonomous Task Execution**: Priority-based task queue with automatic execution
- **Intelligent Error Recovery**: Automatic retry with exponential backoff
- **Event-Driven Architecture**: Flexible event system for custom integrations

### Integration Framework
- **Plugin Architecture**: Extensible integration system for external services
- **Multiple Integration Types**: API, Webhook, and custom integrations
- **Connection Management**: Efficient resource pooling and management
- **Health Monitoring**: Automatic health checks for all integrations

### Reliability & Efficiency
- **Configuration Management**: Environment-specific configuration with hot-reloading
- **Advanced Caching**: LRU/LFU cache strategies with TTL support
- **Async Operations**: Full async/await support for concurrent processing
- **Comprehensive Testing**: Complete test suite with 100 unit tests

## 📦 Quick Start

```bash
# Clone the repository
git clone https://github.com/bf56rrxbrs-crypto/agent-ai.git
cd agent-ai

# Run the demo (Python 3.7+)
python main.py

# Run tests
python -m unittest discover -s . -p "test_*.py"
```

### Using the iOS Agent

```python
import asyncio
from ios_agent import IOSAgent
from autonomous_agent import TaskPriority

async def main():
    agent = IOSAgent(agent_id="my-iphone-agent")
    await agent.start()

    # Store persistent memories
    agent.remember("User prefers dark mode", importance=0.9)

    # Execute instructions with forward-thinking planning
    result = await agent.execute_instruction(
        "Check notifications and prioritize messages",
        priority=TaskPriority.HIGH,
        use_planning=True,
    )

    # Use iOS device capabilities
    await agent.use_capability("focus_mode_control")

    # Recall memories from any session
    memories = agent.recall("dark mode")

    await agent.stop()

asyncio.run(main())
```

## 📖 Documentation

See [USAGE.md](USAGE.md) for comprehensive documentation, examples, and API reference.

## 🏗️ Architecture

- **ios_agent.py** - iPhone 17 Pro iOS agent combining all capabilities
- **forward_thinking_engine.py** - Forward-thinking structural loop engine with plan-execute-evaluate cycles
- **persistent_memory.py** - Cross-session persistent memory with JSON-backed storage
- **autonomous_agent.py** - Core autonomous agent with task scheduling and execution
- **integration_manager.py** - Plugin-based integration framework
- **config_manager.py** - Configuration management with validation
- **cache_manager.py** - Multi-strategy caching system
- **main.py** - Demo showcasing all features including iOS agent

## ✅ All Tests Passing

100 unit tests covering all major functionality:
- iOS agent operations and device capabilities
- Forward-thinking planning engine
- Persistent memory storage and recall
- Autonomous agent operations
- Integration management
- Configuration handling
- Cache strategies (LRU/LFU)

## 🔧 Requirements

Python 3.7+ (no external dependencies required - uses only standard library)

## 📝 License

Part of the bf56rrxbrs-crypto/agent-ai repository.
