//
//  NLPProcessor.swift
//  AgentAI
//
//  Natural Language Processing Module
//  Handles intent recognition and entity extraction
//

import Foundation
import NaturalLanguage

class NLPProcessor {
    
    // MARK: - Properties
    private let sentimentPredictor: NLSentimentPredictor?
    private let languageRecognizer: NLLanguageRecognizer
    private let tagger: NLTagger
    
    // MARK: - Initialization
    init() {
        self.sentimentPredictor = try? NLSentimentPredictor(mlModel: NLModel())
        self.languageRecognizer = NLLanguageRecognizer()
        self.tagger = NLTagger(tagSchemes: [.nameType, .lexicalClass])
    }
    
    // MARK: - Public Methods
    
    /// Analyze user intent from natural language input
    func analyzeIntent(_ text: String) async -> Intent {
        // Detect language
        let language = detectLanguage(text)
        
        // Extract entities
        let entities = extractEntities(from: text)
        
        // Determine intent type
        let intentType = classifyIntent(text, entities: entities)
        
        // Calculate confidence
        let confidence = calculateConfidence(text: text, intentType: intentType)
        
        // Detect patterns for learning
        let pattern = detectPattern(text)
        
        return Intent(
            type: intentType,
            entities: entities,
            confidence: confidence,
            pattern: pattern
        )
    }
    
    /// Extract sentiment from text
    func analyzeSentiment(_ text: String) -> String {
        guard let predictor = sentimentPredictor else {
            return "neutral"
        }
        
        let sentiment = predictor.predict(text)
        return sentiment.rawValue
    }
    
    // MARK: - Private Methods
    
    private func detectLanguage(_ text: String) -> String {
        languageRecognizer.processString(text)
        guard let language = languageRecognizer.dominantLanguage else {
            return "en"
        }
        return language.rawValue
    }
    
    private func extractEntities(from text: String) -> [String: Any] {
        var entities: [String: Any] = [:]
        
        tagger.string = text
        
        // Extract named entities
        let range = text.startIndex..<text.endIndex
        let options: NLTagger.Options = [.omitWhitespace, .omitPunctuation]
        
        tagger.enumerateTags(in: range, unit: .word, scheme: .nameType, options: options) { tag, tokenRange in
            guard let tag = tag else { return true }
            
            let entity = String(text[tokenRange])
            
            switch tag {
            case .personalName:
                entities["person"] = entity
            case .placeName:
                entities["location"] = entity
            case .organizationName:
                entities["organization"] = entity
            default:
                break
            }
            
            return true
        }
        
        // Extract dates and times
        extractDateTimeEntities(from: text, into: &entities)
        
        return entities
    }
    
    private func extractDateTimeEntities(from text: String, into entities: inout [String: Any]) {
        let detector = try? NSDataDetector(types: NSTextCheckingResult.CheckingType.date.rawValue)
        let matches = detector?.matches(in: text, options: [], range: NSRange(location: 0, length: text.utf16.count))
        
        if let match = matches?.first, let date = match.date {
            entities["datetime"] = date
        }
    }
    
    private func classifyIntent(_ text: String, entities: [String: Any]) -> IntentType {
        let lowercasedText = text.lowercased()
        
        // Scheduling keywords
        let schedulingKeywords = ["schedule", "calendar", "meeting", "appointment", "remind", "event"]
        if schedulingKeywords.contains(where: { lowercasedText.contains($0) }) || entities["datetime"] != nil {
            return .scheduling
        }
        
        // Task management keywords
        let taskKeywords = ["task", "todo", "reminder", "complete", "finish", "create", "add"]
        if taskKeywords.contains(where: { lowercasedText.contains($0) }) {
            return .taskManagement
        }
        
        // Communication keywords
        let commKeywords = ["message", "text", "call", "email", "send", "contact"]
        if commKeywords.contains(where: { lowercasedText.contains($0) }) {
            return .communication
        }
        
        // Information retrieval keywords
        let infoKeywords = ["what", "when", "where", "who", "how", "why", "find", "search", "tell me"]
        if infoKeywords.contains(where: { lowercasedText.contains($0) }) {
            return .informationRetrieval
        }
        
        return .general
    }
    
    private func calculateConfidence(text: String, intentType: IntentType) -> Double {
        // Simple confidence calculation based on text length and clarity
        let wordCount = text.components(separatedBy: .whitespaces).count
        
        var confidence = 0.5
        
        // Longer, well-formed sentences have higher confidence
        if wordCount >= 3 && wordCount <= 20 {
            confidence += 0.3
        }
        
        // Specific intent types have higher confidence
        if intentType != .general {
            confidence += 0.2
        }
        
        return min(confidence, 1.0)
    }
    
    private func detectPattern(_ text: String) -> String? {
        // Detect common patterns for learning
        let lowercasedText = text.lowercased()
        
        if lowercasedText.hasPrefix("remind me") {
            return "reminder_request"
        } else if lowercasedText.hasPrefix("schedule") {
            return "schedule_request"
        } else if lowercasedText.hasPrefix("send") {
            return "send_request"
        } else if lowercasedText.hasPrefix("what") || lowercasedText.hasPrefix("tell me") {
            return "information_request"
        }
        
        return nil
    }
}

// MARK: - NLModel Extension
extension NLModel {
    convenience init() {
        // This would load a custom trained model
        // For now, using default initialization
        self.init(contentsOf: Bundle.main.bundleURL)!
    }
}
