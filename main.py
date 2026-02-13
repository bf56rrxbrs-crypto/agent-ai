"""
Main entry point for the Autonomous AI Agent.

This module demonstrates the usage of all autonomous features and integrations,
including advanced AI capabilities.
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

# Import advanced features
from personality_manager import PersonalityManager, PersonalityTrait
from intent_recognizer import IntentRecognizer
from context_manager import ContextManager
from creative_writer import CreativeWriter, WritingTone, ContentType
from multimodal_handler import MultimodalHandler, ImageStyle, TTSVoice, AudioFormat
from learning_system import LearningSystem, FeedbackType, PerformanceMetric
from collaboration_integrations import CollaborationManager, CollaborationPlatform, MessagePriority
from emotion_analyzer import EmotionAnalyzer, Emotion
from security_manager import SecurityManager, DataClassification
from user_profiling import UserProfilingSystem, UserMoodState


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
    
    # 10. Advanced Features Demo
    print("\n10. Advanced AI Features Demo...")
    
    # Personality Manager
    print("\n  10.1 Personality Manager:")
    personality_mgr = PersonalityManager()
    personality_mgr.set_active_profile("empathetic-001")
    profile = personality_mgr.get_active_profile()
    print(f"    ✓ Active profile: {profile.name}")
    
    response = personality_mgr.adjust_response("Here is your answer.")
    print(f"    ✓ Adjusted response: {response}")
    
    # Intent Recognition
    print("\n  10.2 Intent Recognition:")
    intent_recognizer = IntentRecognizer()
    intent = intent_recognizer.recognize("What is the weather today?")
    print(f"    ✓ Recognized intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")
    
    # Context Management
    print("\n  10.3 Context Management:")
    context_mgr = ContextManager()
    context = context_mgr.create_context("demo-ctx-001", user_id="demo-user")
    context_mgr.update_context("demo-ctx-001", "Hello", "Hi there!", intent="greeting")
    summary = context_mgr.get_context_summary("demo-ctx-001")
    print(f"    ✓ Context created with {summary['turn_count']} turn(s)")
    
    # Creative Writer
    print("\n  10.4 Creative Writing:")
    writer = CreativeWriter()
    content = writer.generate_content("email-professional", {
        "recipient": "Team",
        "purpose": "share updates",
        "body": "The project is progressing well.",
        "sender": "AI Agent"
    })
    print(f"    ✓ Generated email ({len(content)} chars)")
    
    # A/B Testing
    variants = ["Version A: Great product!", "Version B: Amazing solution!"]
    ab_test = writer.create_ab_test("test-001", variants)
    print(f"    ✓ Created A/B test with {ab_test['variant_count']} variants")
    
    # Multimodal Handler
    print("\n  10.5 Multimodal Capabilities:")
    mm_handler = MultimodalHandler()
    mm_handler.enable_voice_commands()
    voice_cmd = mm_handler.process_voice_command(None, "Create a new task")
    print(f"    ✓ Processed voice command: {voice_cmd.command_type.value}")
    
    img_request = mm_handler.generate_image("A futuristic AI assistant", ImageStyle.ARTISTIC)
    print(f"    ✓ Image generation request: {img_request['request_id']}")
    
    # Text-to-Speech
    mm_handler.enable_tts()
    tts_result = mm_handler.text_to_speech(
        "Welcome to the AI assistant demo!",
        voice=TTSVoice.FEMALE_NEUTRAL,
        audio_format=AudioFormat.MP3
    )
    print(f"    ✓ TTS generated: {tts_result['request_id']} ({tts_result['estimated_duration']:.1f}s)")
    
    # Learning System
    print("\n  10.6 Learning System:")
    learning_sys = LearningSystem()
    learning_sys.record_feedback(FeedbackType.POSITIVE, rating=4.5, comment="Excellent!")
    learning_sys.record_feedback(FeedbackType.POSITIVE, rating=5.0, comment="Perfect!")
    feedback_summary = learning_sys.get_feedback_summary()
    print(f"    ✓ Recorded {feedback_summary['total']} feedback entries")
    print(f"    ✓ Average rating: {feedback_summary['average_rating']:.1f}/5.0")
    
    # Collaboration Integrations
    print("\n  10.7 Collaboration Integrations:")
    collab_mgr = CollaborationManager()
    await collab_mgr.add_integration(CollaborationPlatform.SLACK, {"workspace": "demo"})
    msg_id = await collab_mgr.send_message(
        CollaborationPlatform.SLACK,
        "general",
        "AI Agent is now online!",
        MessagePriority.NORMAL
    )
    print(f"    ✓ Sent message to Slack: {msg_id}")
    
    # Emotion Analysis
    print("\n  10.8 Emotion Analysis:")
    emotion_analyzer = EmotionAnalyzer()
    analysis = emotion_analyzer.analyze_emotion("I am so happy and excited about this!")
    print(f"    ✓ Detected emotion: {analysis.primary_emotion.value}")
    print(f"    ✓ Sentiment: {analysis.sentiment.value} (score: {analysis.sentiment_score:.2f})")
    
    modified_response = emotion_analyzer.modify_response_for_emotion(
        "Here is your result.",
        analysis.primary_emotion
    )
    print(f"    ✓ Modified response: {modified_response}")
    
    # Security Manager
    print("\n  10.9 Security & Privacy:")
    security_mgr = SecurityManager()
    
    # Encrypt data
    encrypted = security_mgr.encrypt_data("Confidential information")
    print(f"    ✓ Encrypted data with key: {encrypted['key_id']}")
    
    # Register data asset
    asset = security_mgr.register_data_asset(
        "demo-asset-001",
        DataClassification.CONFIDENTIAL,
        encrypted=True,
        owner="demo-user"
    )
    print(f"    ✓ Registered data asset: {asset.asset_id}")
    
    # Check GDPR compliance
    compliance = security_mgr.check_gdpr_compliance("demo-asset-001")
    print(f"    ✓ GDPR compliance: {'✓ Compliant' if compliance['compliant'] else '✗ Non-compliant'}")
    
    # Check CCPA compliance
    ccpa_compliance = security_mgr.check_ccpa_compliance("demo-asset-001")
    print(f"    ✓ CCPA compliance: {'✓ Compliant' if ccpa_compliance['compliant'] else '✗ Non-compliant'}")
    
    # Differential privacy
    sensitive_data = [100.0, 200.0, 150.0, 175.0, 225.0]
    private_mean = security_mgr.aggregate_with_privacy(sensitive_data, "mean", epsilon=1.0)
    print(f"    ✓ Private mean (ε=1.0): {private_mean:.2f} (actual: {sum(sensitive_data)/len(sensitive_data):.2f})")
    
    # Privacy report
    privacy_report = security_mgr.generate_privacy_report()
    print(f"    ✓ Privacy report: {privacy_report['total_assets']} assets, "
          f"{privacy_report['encryption_rate']:.0%} encrypted")
    
    # User Profiling System
    print("\n  10.10 User Profiling & Adaptive Personalization:")
    user_profiling = UserProfilingSystem(storage_path="demo_user_profiles.json")
    
    # Create user profile
    user_profile = user_profiling.create_profile("user-demo-001", name="Demo User")
    user_profiling.update_preferences("user-demo-001", {
        "preferred_tone": "friendly",
        "response_length": "medium"
    })
    print(f"    ✓ Created user profile: {user_profile.name}")
    
    # Track interactions
    user_profiling.track_interaction(
        "user-demo-001",
        topic="AI features",
        duration=5.2,
        detected_mood=UserMoodState.CURIOUS
    )
    print(f"    ✓ Tracked interaction with mood detection")
    
    # Mood detection
    mood = user_profiling.detect_mood_from_text("I need help with this urgent issue!")
    print(f"    ✓ Detected mood from text: {mood.value}")
    
    # Adaptive response
    original_response = "Here are the features you requested."
    adapted_response = user_profiling.adapt_response_to_user(
        "user-demo-001",
        original_response,
        current_mood=UserMoodState.HAPPY
    )
    print(f"    ✓ Adapted response: {adapted_response}")
    
    # User insights
    insights = user_profiling.get_user_insights("user-demo-001")
    print(f"    ✓ User insights: {insights['total_interactions']} interactions")
    
    # 11. Display comprehensive statistics
    print("\n11. Advanced Features Statistics:")
    print(f"  Personality Manager:")
    print(f"    - Profiles: {len(personality_mgr.profiles)}")
    print(f"    - Interactions: {len(personality_mgr.interaction_history)}")
    
    print(f"  Intent Recognizer:")
    intent_stats = intent_recognizer.get_stats()
    print(f"    - Total recognitions: {intent_stats['total_recognitions']}")
    
    print(f"  Context Manager:")
    context_stats = context_mgr.get_stats()
    print(f"    - Active contexts: {context_stats['active_contexts']}")
    print(f"    - Total turns: {context_stats['total_turns']}")
    
    print(f"  Learning System:")
    learning_stats = learning_sys.get_stats()
    print(f"    - Total feedback: {learning_stats['total_feedback']}")
    print(f"    - Recommendations: {learning_stats['recommendations_count']}")
    
    print(f"  Collaboration Manager:")
    collab_stats = collab_mgr.get_stats()
    print(f"    - Active integrations: {collab_stats['active_integrations']}")
    print(f"    - Total messages: {collab_stats['total_messages']}")
    
    print(f"  Emotion Analyzer:")
    emotion_stats = emotion_analyzer.get_stats()
    print(f"    - Total analyses: {emotion_stats['total_analyses']}")
    
    print(f"  Security Manager:")
    security_stats = security_mgr.get_stats()
    print(f"    - Total assets: {security_stats['total_assets']}")
    print(f"    - Encrypted assets: {security_stats['encrypted_assets']}")
    
    print(f"  User Profiling:")
    profiling_stats = user_profiling.get_stats()
    print(f"    - Total profiles: {profiling_stats['total_profiles']}")
    print(f"    - Total interactions: {profiling_stats['total_interactions']}")
    
    # 12. Graceful shutdown
    print("\n12. Shutting down agent...")
    await agent.stop()
    print("✓ Agent stopped gracefully")
    
    print("\n" + "=" * 60)
    print("🎉 Complete Demo with Advanced Features Finished!")
    print("=" * 60)
    print("\nAll 10 advanced AI features demonstrated:")
    print("  1. ✓ Personality & Behavior Customization")
    print("  2. ✓ Intent Recognition & Context Awareness")
    print("  3. ✓ Creative Writing & Personalization")
    print("  4. ✓ Multimodal Capabilities (Voice, TTS, & Image)")
    print("  5. ✓ Auto-Improving Learning System")
    print("  6. ✓ Real-Time Collaboration Integrations")
    print("  7. ✓ Emotional Intelligence")
    print("  8. ✓ Data Security with Differential Privacy")
    print("  9. ✓ User Profiling & Adaptive Personalization")
    print(" 10. ✓ GDPR & CCPA Privacy Compliance")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        logging.exception("Fatal error in main")
