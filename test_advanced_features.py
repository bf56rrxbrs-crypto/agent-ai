"""
Unit tests for all advanced features modules
"""

import unittest
import asyncio
from multimodal_handler import MultimodalHandler, VoiceCommandType, ImageStyle, TTSVoice, AudioFormat
from learning_system import LearningSystem, FeedbackType, PerformanceMetric
from emotion_analyzer import EmotionAnalyzer, Emotion, Sentiment
from security_manager import SecurityManager, DataClassification, EncryptionAlgorithm
from collaboration_integrations import CollaborationManager, CollaborationPlatform, MessagePriority


class TestMultimodalHandler(unittest.TestCase):
    """Test MultimodalHandler"""
    
    def setUp(self):
        self.handler = MultimodalHandler()
    
    def test_voice_commands(self):
        """Test voice command processing"""
        self.handler.enable_voice_commands()
        self.assertTrue(self.handler.voice_enabled)
        
        cmd = self.handler.process_voice_command(None, "What is the time?")
        self.assertEqual(cmd.command_type, VoiceCommandType.QUERY)
    
    def test_image_generation(self):
        """Test image generation request"""
        result = self.handler.generate_image("A beautiful sunset", ImageStyle.REALISTIC)
        
        self.assertIn("request_id", result)
        self.assertEqual(result["status"], "pending")
    
    def test_tts_functionality(self):
        """Test text-to-speech"""
        self.handler.enable_tts()
        self.assertTrue(self.handler.tts_enabled)
        
        result = self.handler.text_to_speech(
            "Hello, this is a test",
            voice=TTSVoice.FEMALE_NEUTRAL,
            audio_format=AudioFormat.MP3
        )
        
        self.assertIn("request_id", result)
        self.assertIn("audio_url", result)
        self.assertEqual(result["status"], "completed")
    
    def test_tts_disabled(self):
        """Test TTS when disabled"""
        result = self.handler.text_to_speech("Test")
        self.assertIn("error", result)
    
    def test_speech_to_text_stub(self):
        """Test speech-to-text stub"""
        result = self.handler.speech_to_text_api_example("audio.wav")
        
        self.assertIn("transcription", result)
        self.assertIn("confidence", result)
    
    def test_get_stats(self):
        """Test getting statistics"""
        self.handler.enable_tts()
        self.handler.process_voice_command(None, "Hello")
        self.handler.text_to_speech("Test")
        
        stats = self.handler.get_stats()
        
        self.assertIn("total_voice_commands", stats)
        self.assertIn("total_tts_requests", stats)
        self.assertGreater(stats["total_voice_commands"], 0)
        self.assertGreater(stats["total_tts_requests"], 0)


class TestLearningSystem(unittest.TestCase):
    """Test LearningSystem"""
    
    def setUp(self):
        self.system = LearningSystem()
    
    def test_record_feedback(self):
        """Test recording feedback"""
        entry = self.system.record_feedback(
            FeedbackType.POSITIVE,
            user_id="user-1",
            rating=4.5,
            comment="Great!"
        )
        
        self.assertEqual(entry.feedback_type, FeedbackType.POSITIVE)
        self.assertEqual(len(self.system.feedback), 1)
    
    def test_feedback_summary(self):
        """Test getting feedback summary"""
        self.system.record_feedback(FeedbackType.POSITIVE, rating=5.0)
        self.system.record_feedback(FeedbackType.NEGATIVE, rating=2.0)
        
        summary = self.system.get_feedback_summary()
        
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["average_rating"], 3.5)
    
    def test_performance_tracking(self):
        """Test tracking performance"""
        metrics = {
            PerformanceMetric.ACCURACY: 0.95,
            PerformanceMetric.RESPONSE_TIME: 0.5
        }
        
        self.system.track_performance(metrics)
        self.assertEqual(len(self.system.performance_history), 1)
    
    def test_improvement_recommendations(self):
        """Test getting improvement recommendations"""
        # Add negative feedback to trigger recommendations
        for _ in range(15):
            self.system.record_feedback(FeedbackType.NEGATIVE, rating=2.0)
        
        recommendations = self.system.get_improvement_recommendations()
        self.assertIsInstance(recommendations, list)


class TestEmotionAnalyzer(unittest.TestCase):
    """Test EmotionAnalyzer"""
    
    def setUp(self):
        self.analyzer = EmotionAnalyzer()
    
    def test_analyze_joy(self):
        """Test detecting joy emotion"""
        analysis = self.analyzer.analyze_emotion("I am so happy and excited!")
        
        self.assertEqual(analysis.primary_emotion, Emotion.JOY)
        self.assertGreater(analysis.confidence, 0)
    
    def test_analyze_sadness(self):
        """Test detecting sadness emotion"""
        analysis = self.analyzer.analyze_emotion("I feel so sad and disappointed")
        
        self.assertEqual(analysis.primary_emotion, Emotion.SADNESS)
    
    def test_sentiment_positive(self):
        """Test positive sentiment detection"""
        analysis = self.analyzer.analyze_emotion("This is great and wonderful!")
        
        self.assertIn(analysis.sentiment, [Sentiment.POSITIVE, Sentiment.VERY_POSITIVE])
        self.assertGreater(analysis.sentiment_score, 0)
    
    def test_sentiment_negative(self):
        """Test negative sentiment detection"""
        analysis = self.analyzer.analyze_emotion("This is terrible and awful")
        
        self.assertIn(analysis.sentiment, [Sentiment.NEGATIVE, Sentiment.VERY_NEGATIVE])
        self.assertLess(analysis.sentiment_score, 0)
    
    def test_modify_response(self):
        """Test response modification based on emotion"""
        original = "Here is your answer."
        
        modified = self.analyzer.modify_response_for_emotion(original, Emotion.SADNESS)
        self.assertIn("understand", modified.lower())
        
        modified = self.analyzer.modify_response_for_emotion(original, Emotion.ANGER)
        self.assertIn("apologize", modified.lower())
    
    def test_conversation_mood(self):
        """Test analyzing conversation mood"""
        messages = [
            "I'm happy",
            "This is great",
            "Wonderful!"
        ]
        
        mood = self.analyzer.analyze_conversation_mood(messages)
        
        self.assertIn("overall_sentiment", mood)
        self.assertEqual(mood["dominant_emotion"], "joy")


class TestSecurityManager(unittest.TestCase):
    """Test SecurityManager"""
    
    def setUp(self):
        self.manager = SecurityManager()
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        original_data = "sensitive information"
        
        encrypted = self.manager.encrypt_data(original_data)
        self.assertIn("encrypted_data", encrypted)
        self.assertIn("key_id", encrypted)
        
        decrypted = self.manager.decrypt_data(
            encrypted["encrypted_data"],
            encrypted["key_id"]
        )
        
        self.assertEqual(decrypted, original_data)
    
    def test_hash_data(self):
        """Test data hashing"""
        data = "test data"
        hash1 = self.manager.hash_data(data)
        hash2 = self.manager.hash_data(data)
        
        # Same input should produce same hash
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA-256 produces 64 hex chars
    
    def test_register_asset(self):
        """Test registering data asset"""
        asset = self.manager.register_data_asset(
            "asset-001",
            DataClassification.CONFIDENTIAL,
            encrypted=True,
            owner="user-1"
        )
        
        self.assertEqual(asset.asset_id, "asset-001")
        self.assertIn("asset-001", self.manager.data_assets)
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance check"""
        # Register compliant asset
        self.manager.register_data_asset(
            "asset-002",
            DataClassification.CONFIDENTIAL,
            encrypted=True,
            owner="user-1",
            retention_days=365
        )
        
        compliance = self.manager.check_gdpr_compliance("asset-002")
        self.assertTrue(compliance["compliant"])
    
    def test_anonymize_pii(self):
        """Test PII anonymization"""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        
        anonymized = self.manager.anonymize_pii(data)
        
        self.assertNotEqual(anonymized["name"], "John Doe")
        self.assertNotEqual(anonymized["email"], "john@example.com")
        self.assertEqual(anonymized["age"], 30)  # Non-PII unchanged
    
    def test_differential_privacy(self):
        """Test differential privacy mechanism"""
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        # Apply differential privacy
        noisy_data = self.manager.apply_differential_privacy(
            data,
            epsilon=1.0,
            sensitivity=1.0
        )
        
        # Check that we got back the same number of values
        self.assertEqual(len(noisy_data), len(data))
        
        # Values should be different due to noise
        # (there's a tiny chance they could be the same, but very unlikely)
        differences = sum(1 for i in range(len(data)) if noisy_data[i] != data[i])
        self.assertGreater(differences, 0)
    
    def test_aggregate_with_privacy(self):
        """Test aggregation with differential privacy"""
        data = [100.0, 200.0, 300.0, 400.0, 500.0]
        
        # Test mean aggregation
        noisy_mean = self.manager.aggregate_with_privacy(data, "mean", epsilon=1.0)
        self.assertIsInstance(noisy_mean, float)
        
        # Test sum aggregation
        noisy_sum = self.manager.aggregate_with_privacy(data, "sum", epsilon=1.0)
        self.assertIsInstance(noisy_sum, float)
        
        # Test count aggregation
        noisy_count = self.manager.aggregate_with_privacy(data, "count", epsilon=1.0)
        self.assertIsInstance(noisy_count, float)
    
    def test_ccpa_compliance(self):
        """Test CCPA compliance check"""
        # Register asset
        self.manager.register_data_asset(
            "asset-ccpa-001",
            DataClassification.CONFIDENTIAL,
            encrypted=True,
            owner="data-manager",
            retention_days=365
        )
        
        compliance = self.manager.check_ccpa_compliance("asset-ccpa-001")
        
        self.assertIn("regulation", compliance)
        self.assertEqual(compliance["regulation"], "CCPA")
        self.assertTrue(compliance["compliant"])
    
    def test_privacy_report(self):
        """Test generating privacy report"""
        self.manager.register_data_asset(
            "asset-003",
            DataClassification.PUBLIC,
            encrypted=False
        )
        
        report = self.manager.generate_privacy_report()
        
        self.assertIn("total_assets", report)
        self.assertIn("gdpr_compliance_rate", report)
    
    def test_audit_log(self):
        """Test audit logging"""
        self.manager.encrypt_data("test")
        
        audit_log = self.manager.get_audit_log()
        self.assertGreater(len(audit_log), 0)


class TestCollaborationIntegrations(unittest.TestCase):
    """Test CollaborationManager"""
    
    def setUp(self):
        self.manager = CollaborationManager()
    
    def test_add_integration(self):
        """Test adding integration"""
        async def test():
            await self.manager.add_integration(
                CollaborationPlatform.SLACK,
                {"workspace": "test", "bot_token": "xoxb-test"}
            )
            
            integrations = self.manager.list_integrations()
            self.assertEqual(len(integrations), 1)
        
        asyncio.run(test())
    
    def test_send_message(self):
        """Test sending message"""
        async def test():
            await self.manager.add_integration(
                CollaborationPlatform.SLACK,
                {"workspace": "test"}
            )
            
            msg_id = await self.manager.send_message(
                CollaborationPlatform.SLACK,
                "general",
                "Hello team!",
                MessagePriority.NORMAL
            )
            
            self.assertIsNotNone(msg_id)
        
        asyncio.run(test())
    
    def test_create_document(self):
        """Test creating document"""
        async def test():
            await self.manager.add_integration(
                CollaborationPlatform.GOOGLE_DOCS,
                {"credentials": "test"}
            )
            
            doc_id = await self.manager.create_document(
                CollaborationPlatform.GOOGLE_DOCS,
                "Test Document",
                "This is test content"
            )
            
            self.assertIsNotNone(doc_id)
        
        asyncio.run(test())
    
    def test_get_stats(self):
        """Test getting statistics"""
        async def test():
            await self.manager.add_integration(
                CollaborationPlatform.SLACK,
                {"workspace": "test"}
            )
            
            stats = self.manager.get_stats()
            self.assertEqual(stats["active_integrations"], 1)
        
        asyncio.run(test())


if __name__ == "__main__":
    unittest.main()
