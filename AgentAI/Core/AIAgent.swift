//
//  AIAgent.swift
//  AgentAI
//
//  Core AI Agent - Orchestrates all AI capabilities
//

import Foundation
import Combine
import SwiftUI

// MARK: - Chat Message Model
struct ChatMessage: Identifiable, Codable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
    let metadata: String?
    
    init(id: UUID = UUID(), content: String, isUser: Bool, timestamp: Date = Date(), metadata: String? = nil) {
        self.id = id
        self.content = content
        self.isUser = isUser
        self.timestamp = timestamp
        self.metadata = metadata
    }
}

// MARK: - User Preference Model
struct UserPreference: Codable {
    var preferredLanguage: String
    var preferredCommunicationStyle: String
    var enabledIntegrations: [String]
    var learningData: [String: Any]
    
    enum CodingKeys: String, CodingKey {
        case preferredLanguage
        case preferredCommunicationStyle
        case enabledIntegrations
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        preferredLanguage = try container.decode(String.self, forKey: .preferredLanguage)
        preferredCommunicationStyle = try container.decode(String.self, forKey: .preferredCommunicationStyle)
        enabledIntegrations = try container.decode([String].self, forKey: .enabledIntegrations)
        learningData = [:]
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(preferredLanguage, forKey: .preferredLanguage)
        try container.encode(preferredCommunicationStyle, forKey: .preferredCommunicationStyle)
        try container.encode(enabledIntegrations, forKey: .enabledIntegrations)
    }
    
    init() {
        self.preferredLanguage = "English"
        self.preferredCommunicationStyle = "Conversational"
        self.enabledIntegrations = ["Calendar", "Reminders", "Messages"]
        self.learningData = [:]
    }
}

// MARK: - AI Agent Main Class
@MainActor
class AIAgent: ObservableObject {
    // MARK: - Published Properties
    @Published var conversationHistory: [ChatMessage] = []
    @Published var status: String = "Ready"
    @Published var isActive: Bool = true
    @Published var userPreferences: UserPreference = UserPreference()
    
    // MARK: - Core Components
    private let modelManager: ModelManager
    private let nlpProcessor: NLPProcessor
    private let appIntegrationManager: AppIntegrationManager
    private let workflowOrchestrator: WorkflowOrchestrator
    
    // MARK: - Initialization
    init() {
        self.modelManager = ModelManager()
        self.nlpProcessor = NLPProcessor()
        self.appIntegrationManager = AppIntegrationManager()
        self.workflowOrchestrator = WorkflowOrchestrator()
        
        loadUserPreferences()
        initializeAgent()
    }
    
    // MARK: - Public Methods
    
    /// Process user command with natural language understanding
    func processCommand(_ command: String) async {
        // Add user message to history
        let userMessage = ChatMessage(content: command, isUser: true)
        conversationHistory.append(userMessage)
        
        status = "Processing..."
        
        do {
            // Step 1: Analyze command with NLP
            let intent = await nlpProcessor.analyzeIntent(command)
            
            // Step 2: Personalize based on user preferences
            let personalizedContext = personalizeResponse(for: intent)
            
            // Step 3: Execute workflow based on intent
            let response = try await workflowOrchestrator.executeWorkflow(
                intent: intent,
                context: personalizedContext,
                integrationManager: appIntegrationManager,
                modelManager: modelManager
            )
            
            // Step 4: Learn from interaction
            updatePreferences(from: intent, response: response)
            
            // Add agent response to history
            let agentMessage = ChatMessage(
                content: response.message,
                isUser: false,
                metadata: response.metadata
            )
            conversationHistory.append(agentMessage)
            
            status = "Ready"
        } catch {
            let errorMessage = ChatMessage(
                content: "I encountered an error: \(error.localizedDescription)",
                isUser: false,
                metadata: "Error"
            )
            conversationHistory.append(errorMessage)
            status = "Error occurred"
        }
    }
    
    /// Clear conversation history
    func clearHistory() {
        conversationHistory.removeAll()
        status = "History cleared"
    }
    
    /// Show settings interface
    func showSettings() {
        status = "Settings opened"
        // This would typically navigate to a settings view
    }
    
    /// Show app integrations
    func showIntegrations() {
        status = "Integrations opened"
        // This would typically navigate to integrations view
    }
    
    // MARK: - Private Methods
    
    private func initializeAgent() {
        status = "Initializing AI models..."
        
        Task {
            await modelManager.loadModels()
            await appIntegrationManager.setupIntegrations(enabledApps: userPreferences.enabledIntegrations)
            
            // Send welcome message
            let welcomeMessage = ChatMessage(
                content: "Hello! I'm your comprehensive AI agent. I can help you with tasks, scheduling, communication, and much more. How can I assist you today?",
                isUser: false,
                metadata: "System"
            )
            conversationHistory.append(welcomeMessage)
            
            status = "Ready"
        }
    }
    
    private func personalizeResponse(for intent: Intent) -> PersonalizationContext {
        return PersonalizationContext(
            language: userPreferences.preferredLanguage,
            communicationStyle: userPreferences.preferredCommunicationStyle,
            userHistory: conversationHistory,
            learningData: userPreferences.learningData
        )
    }
    
    private func updatePreferences(from intent: Intent, response: WorkflowResponse) {
        // Learn from user interactions
        // This would implement machine learning logic to improve personalization
        
        // For now, just track interaction patterns
        if let pattern = intent.pattern {
            userPreferences.learningData[pattern] = (userPreferences.learningData[pattern] as? Int ?? 0) + 1
        }
        
        saveUserPreferences()
    }
    
    private func loadUserPreferences() {
        if let data = UserDefaults.standard.data(forKey: "UserPreferences"),
           let preferences = try? JSONDecoder().decode(UserPreference.self, from: data) {
            self.userPreferences = preferences
        }
    }
    
    private func saveUserPreferences() {
        if let data = try? JSONEncoder().encode(userPreferences) {
            UserDefaults.standard.set(data, forKey: "UserPreferences")
        }
    }
}

// MARK: - Supporting Models

struct Intent {
    let type: IntentType
    let entities: [String: Any]
    let confidence: Double
    let pattern: String?
}

enum IntentType {
    case scheduling
    case taskManagement
    case communication
    case informationRetrieval
    case general
}

struct PersonalizationContext {
    let language: String
    let communicationStyle: String
    let userHistory: [ChatMessage]
    let learningData: [String: Any]
}

struct WorkflowResponse {
    let message: String
    let metadata: String?
    let success: Bool
}
