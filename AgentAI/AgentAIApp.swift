//
//  AgentAIApp.swift
//  AgentAI
//
//  Comprehensive AI Agent for iPhone
//

import SwiftUI

@main
struct AgentAIApp: App {
    @StateObject private var aiAgent = AIAgent()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(aiAgent)
        }
    }
}
