# Agent AI - Comprehensive AI Agent for iPhone

An intelligent AI agent application for iPhone that utilizes multiple models, tools, and resources to perform real tasks autonomously. Includes a **Python-based autonomous agent framework** with forward-thinking structural loop engineering, persistent memory, and iOS-specific device capabilities tailored for iPhone 17 Pro.

## 🚀 Features

### iOS Agent Assistant (iPhone 17 Pro)
- **Forward-Thinking Structural Loop Engineering**: Plan-execute-evaluate cycles with adaptive re-planning for anticipatory multi-step reasoning
- **Persistent Memory**: Cross-session JSON-backed memory with categorized recall, importance scoring, and automatic cleanup
- **iOS Device Capabilities**: 16 capabilities tailored for iPhone 17 Pro including Apple Intelligence, Camera Control, Action Button, Siri integration, Focus modes, Shortcuts automation, Live Activities, HomeKit/Matter, and more
- **Apple Intelligence & On-Device AI**: Leverages A19 Pro Neural Engine (18 cores) for on-device AI processing
- **Reliability Tracking**: Instruction-level success tracking for consistent, dependable execution

### Swift iOS Application
- **Multi-Model AI System**: Leverages multiple AI models for enhanced capabilities
- **Seamless App Integration**: Integrates with Calendar, Reminders, Contacts, and more
- **Advanced NLP**: Sophisticated natural language understanding and processing
- **Agentic Workflows**: Autonomous execution of complex multi-step tasks
- **Personalization Engine**: Learns from user interactions and adapts responses

### Autonomous Agent Framework (Python)
- **Self-Monitoring**: Continuous health checks and status monitoring
- **Autonomous Task Execution**: Priority-based task queue with automatic execution
- **Intelligent Error Recovery**: Automatic retry with exponential backoff
- **Event-Driven Architecture**: Flexible event system for custom integrations

### Integration & Reliability
- **Plugin Architecture**: Extensible integration system for external services
- **Advanced Caching**: LRU/LFU cache strategies with TTL support
- **Configuration Management**: Environment-specific configuration with hot-reloading
- **Comprehensive Testing**: Complete test suite with 100 unit tests

## 📱 iOS Quick Start

1. Open `AgentAI.xcodeproj` in Xcode
2. Build and run on your iPhone (iOS 16.0+)
3. Grant necessary permissions (Calendar, Reminders, Contacts)
4. Start interacting with your AI agent!

## 📦 Python Agent Quick Start

```bash
# Run the demo (Python 3.7+)
python main.py

# Run tests
python -m unittest discover -s . -p "test_*.py"
```

### Using the iOS Agent (Python)

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

## 📚 Documentation

- [Detailed Documentation](AgentAI_README.md) - Complete iOS feature guide
- [Configuration Guide](CONFIGURATION.md) - Setup and customization
- [Usage Guide](USAGE.md) - Python agent documentation and API reference
- [Architecture](ARCHITECTURE.md) - System architecture overview

## 🏗️ Architecture

### Swift iOS Application
- **AIAgent** - Main orchestrator
- **NLPProcessor** - Natural language understanding
- **ModelManager** - Multi-model AI management
- **AppIntegrationManager** - iOS app integrations
- **WorkflowOrchestrator** - Task execution engine

### Python Agent Framework
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

- **iOS App**: iOS 16.0+, Xcode 14.0+, Swift 5.0+
- **Python Agent**: Python 3.7+ (no external dependencies - uses only standard library)

## 🔒 Privacy & Security

- All data stored locally on device
- Explicit permission requests
- No unauthorized external data transmission
- Secure handling of sensitive information

## 📝 License

Part of the bf56rrxbrs-crypto/agent-ai repository.
