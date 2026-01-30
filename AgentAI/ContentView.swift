//
//  ContentView.swift
//  AgentAI
//
//  Main user interface for AI Agent
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var aiAgent: AIAgent
    @State private var userInput: String = ""
    @State private var isProcessing: Bool = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Agent Status Header
                HStack {
                    Image(systemName: "brain.head.profile")
                        .font(.largeTitle)
                        .foregroundColor(.blue)
                    
                    VStack(alignment: .leading) {
                        Text("AI Agent")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text(aiAgent.status)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Circle()
                        .fill(aiAgent.isActive ? Color.green : Color.gray)
                        .frame(width: 12, height: 12)
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                .padding()
                
                // Conversation History
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(aiAgent.conversationHistory) { message in
                            MessageBubble(message: message)
                        }
                    }
                    .padding()
                }
                
                // Input Area
                HStack {
                    TextField("Ask me anything...", text: $userInput)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .disabled(isProcessing)
                    
                    Button(action: {
                        sendMessage()
                    }) {
                        Image(systemName: isProcessing ? "hourglass" : "paperplane.fill")
                            .foregroundColor(.white)
                            .padding(10)
                            .background(Color.blue)
                            .clipShape(Circle())
                    }
                    .disabled(userInput.isEmpty || isProcessing)
                }
                .padding()
            }
            .navigationTitle("Agent AI")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button(action: { aiAgent.clearHistory() }) {
                            Label("Clear History", systemImage: "trash")
                        }
                        
                        Button(action: { aiAgent.showSettings() }) {
                            Label("Settings", systemImage: "gear")
                        }
                        
                        Button(action: { aiAgent.showIntegrations() }) {
                            Label("App Integrations", systemImage: "square.grid.2x2")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
    }
    
    private func sendMessage() {
        guard !userInput.isEmpty else { return }
        
        isProcessing = true
        let message = userInput
        userInput = ""
        
        Task {
            await aiAgent.processCommand(message)
            isProcessing = false
        }
    }
}

struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isUser {
                Spacer()
            }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .padding(12)
                    .background(message.isUser ? Color.blue : Color(.systemGray5))
                    .foregroundColor(message.isUser ? .white : .primary)
                    .cornerRadius(16)
                
                if let metadata = message.metadata {
                    Text(metadata)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            if !message.isUser {
                Spacer()
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AIAgent())
    }
}
