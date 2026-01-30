//
//  WorkflowOrchestrator.swift
//  AgentAI
//
//  Orchestrates agentic workflows and task execution
//

import Foundation

class WorkflowOrchestrator {
    
    // MARK: - Properties
    private var activeWorkflows: [UUID: Workflow] = [:]
    
    // MARK: - Initialization
    init() {}
    
    // MARK: - Public Methods
    
    /// Execute a workflow based on detected intent
    func executeWorkflow(
        intent: Intent,
        context: PersonalizationContext,
        integrationManager: AppIntegrationManager,
        modelManager: ModelManager
    ) async throws -> WorkflowResponse {
        
        let workflow = createWorkflow(for: intent, context: context)
        activeWorkflows[workflow.id] = workflow
        
        defer {
            activeWorkflows.removeValue(forKey: workflow.id)
        }
        
        do {
            let result = try await processWorkflow(
                workflow,
                integrationManager: integrationManager,
                modelManager: modelManager,
                context: context
            )
            
            return WorkflowResponse(
                message: result.message,
                metadata: result.metadata,
                success: true
            )
        } catch {
            return WorkflowResponse(
                message: "Failed to complete workflow: \(error.localizedDescription)",
                metadata: "Error",
                success: false
            )
        }
    }
    
    // MARK: - Private Methods
    
    private func createWorkflow(for intent: Intent, context: PersonalizationContext) -> Workflow {
        let steps: [WorkflowStep]
        
        switch intent.type {
        case .scheduling:
            steps = createSchedulingWorkflow(intent: intent)
        case .taskManagement:
            steps = createTaskManagementWorkflow(intent: intent)
        case .communication:
            steps = createCommunicationWorkflow(intent: intent)
        case .informationRetrieval:
            steps = createInformationRetrievalWorkflow(intent: intent)
        case .general:
            steps = createGeneralWorkflow(intent: intent)
        }
        
        return Workflow(
            id: UUID(),
            type: intent.type,
            steps: steps,
            context: context
        )
    }
    
    private func processWorkflow(
        _ workflow: Workflow,
        integrationManager: AppIntegrationManager,
        modelManager: ModelManager,
        context: PersonalizationContext
    ) async throws -> WorkflowResult {
        
        var results: [String] = []
        
        for step in workflow.steps {
            let stepResult = try await executeStep(
                step,
                integrationManager: integrationManager,
                modelManager: modelManager,
                context: context
            )
            results.append(stepResult)
        }
        
        let finalMessage = generateResponse(
            from: results,
            workflowType: workflow.type,
            context: context
        )
        
        return WorkflowResult(
            message: finalMessage,
            metadata: "Completed \(workflow.steps.count) steps",
            details: results
        )
    }
    
    private func executeStep(
        _ step: WorkflowStep,
        integrationManager: AppIntegrationManager,
        modelManager: ModelManager,
        context: PersonalizationContext
    ) async throws -> String {
        
        switch step.action {
        case .createCalendarEvent(let title, let date):
            let success = try await integrationManager.createCalendarEvent(
                title: title,
                date: date
            )
            return success ? "Created calendar event: \(title)" : "Failed to create event"
            
        case .createReminder(let title, let date):
            let success = try await integrationManager.createReminder(
                title: title,
                dueDate: date
            )
            return success ? "Created reminder: \(title)" : "Failed to create reminder"
            
        case .fetchInformation(let query):
            let info = try await fetchInformation(query: query, integrationManager: integrationManager)
            return info
            
        case .generateResponse(let prompt):
            let response = await modelManager.generateResponse(prompt: prompt, context: context)
            return response
            
        case .findContact(let name):
            if let contact = try await integrationManager.findContact(name: name) {
                return "Found contact: \(contact.givenName) \(contact.familyName)"
            } else {
                return "Contact not found"
            }
            
        case .getUpcomingEvents:
            let events = try await integrationManager.getUpcomingEvents()
            return "Found \(events.count) upcoming events"
        }
    }
    
    private func fetchInformation(
        query: String,
        integrationManager: AppIntegrationManager
    ) async throws -> String {
        
        let lowercasedQuery = query.lowercased()
        
        if lowercasedQuery.contains("weather") {
            let weather = try await integrationManager.fetchWeatherData(location: "Current Location")
            return "The weather is \(weather.condition) with a temperature of \(weather.temperature)°F"
        } else if lowercasedQuery.contains("news") {
            let headlines = try await integrationManager.fetchNewsHeadlines()
            return "Top headlines: \(headlines.map { $0.title }.joined(separator: ", "))"
        } else {
            return "I found information about: \(query)"
        }
    }
    
    private func generateResponse(
        from results: [String],
        workflowType: IntentType,
        context: PersonalizationContext
    ) -> String {
        
        let style = context.communicationStyle.lowercased()
        
        switch workflowType {
        case .scheduling:
            return formatSchedulingResponse(results, style: style)
        case .taskManagement:
            return formatTaskResponse(results, style: style)
        case .communication:
            return formatCommunicationResponse(results, style: style)
        case .informationRetrieval:
            return formatInformationResponse(results, style: style)
        case .general:
            return formatGeneralResponse(results, style: style)
        }
    }
    
    // MARK: - Workflow Creation Methods
    
    private func createSchedulingWorkflow(intent: Intent) -> [WorkflowStep] {
        var steps: [WorkflowStep] = []
        
        if let datetime = intent.entities["datetime"] as? Date {
            let title = intent.entities["title"] as? String ?? "New Event"
            steps.append(WorkflowStep(action: .createCalendarEvent(title: title, date: datetime)))
        }
        
        steps.append(WorkflowStep(action: .getUpcomingEvents))
        
        return steps
    }
    
    private func createTaskManagementWorkflow(intent: Intent) -> [WorkflowStep] {
        var steps: [WorkflowStep] = []
        
        let title = intent.entities["title"] as? String ?? "New Task"
        let datetime = intent.entities["datetime"] as? Date
        
        steps.append(WorkflowStep(action: .createReminder(title: title, date: datetime)))
        
        return steps
    }
    
    private func createCommunicationWorkflow(intent: Intent) -> [WorkflowStep] {
        var steps: [WorkflowStep] = []
        
        if let person = intent.entities["person"] as? String {
            steps.append(WorkflowStep(action: .findContact(name: person)))
        }
        
        return steps
    }
    
    private func createInformationRetrievalWorkflow(intent: Intent) -> [WorkflowStep] {
        let query = intent.entities["query"] as? String ?? "general information"
        return [WorkflowStep(action: .fetchInformation(query: query))]
    }
    
    private func createGeneralWorkflow(intent: Intent) -> [WorkflowStep] {
        let prompt = intent.entities["prompt"] as? String ?? "Help me with this request"
        return [WorkflowStep(action: .generateResponse(prompt: prompt))]
    }
    
    // MARK: - Response Formatting Methods
    
    private func formatSchedulingResponse(_ results: [String], style: String) -> String {
        if style.contains("formal") {
            return "I have completed the scheduling request. \(results.joined(separator: ". "))."
        } else {
            return "Done! \(results.joined(separator: ". "))"
        }
    }
    
    private func formatTaskResponse(_ results: [String], style: String) -> String {
        return "✓ \(results.joined(separator: "\n✓ "))"
    }
    
    private func formatCommunicationResponse(_ results: [String], style: String) -> String {
        return results.joined(separator: "\n")
    }
    
    private func formatInformationResponse(_ results: [String], style: String) -> String {
        return results.joined(separator: "\n\n")
    }
    
    private func formatGeneralResponse(_ results: [String], style: String) -> String {
        return results.joined(separator: " ")
    }
}

// MARK: - Supporting Models

struct Workflow {
    let id: UUID
    let type: IntentType
    let steps: [WorkflowStep]
    let context: PersonalizationContext
}

struct WorkflowStep {
    let action: WorkflowAction
}

enum WorkflowAction {
    case createCalendarEvent(title: String, date: Date)
    case createReminder(title: String, date: Date?)
    case fetchInformation(query: String)
    case generateResponse(prompt: String)
    case findContact(name: String)
    case getUpcomingEvents
}

struct WorkflowResult {
    let message: String
    let metadata: String
    let details: [String]
}
