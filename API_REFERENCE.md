# API Reference

## AIAgent Class

The main orchestrator for all AI capabilities.

### Properties

```swift
@Published var conversationHistory: [ChatMessage]
@Published var status: String
@Published var isActive: Bool
@Published var userPreferences: UserPreference
```

### Methods

#### `processCommand(_ command: String) async`
Processes a user command with natural language understanding.

**Parameters:**
- `command`: The user's natural language command

**Example:**
```swift
await aiAgent.processCommand("Schedule a meeting tomorrow at 2 PM")
```

#### `clearHistory()`
Clears the conversation history.

#### `showSettings()`
Opens the settings interface.

#### `showIntegrations()`
Opens the integrations management interface.

---

## NLPProcessor Class

Handles natural language processing and understanding.

### Methods

#### `analyzeIntent(_ text: String) async -> Intent`
Analyzes user intent from natural language input.

**Parameters:**
- `text`: The input text to analyze

**Returns:** Intent object with type, entities, and confidence

**Example:**
```swift
let intent = await nlpProcessor.analyzeIntent("Remind me to buy milk")
// intent.type == .taskManagement
// intent.entities == ["title": "buy milk"]
```

#### `analyzeSentiment(_ text: String) -> String`
Extracts sentiment from text.

**Parameters:**
- `text`: The input text

**Returns:** Sentiment label ("positive", "negative", or "neutral")

---

## ModelManager Class

Manages multiple AI models for different tasks.

### Methods

#### `loadModels() async`
Loads all AI models asynchronously.

#### `generateResponse(prompt: String, context: PersonalizationContext) async -> String`
Generates a response using AI models.

**Parameters:**
- `prompt`: The input prompt
- `context`: Personalization context for customized responses

**Returns:** Generated response string

#### `classifyIntent(text: String) async -> String`
Classifies the intent of input text.

#### `analyzeSentiment(text: String) async -> SentimentResult`
Analyzes text sentiment with score and label.

#### `summarizeText(text: String, maxLength: Int) async -> String`
Summarizes long text.

#### `translateText(text: String, targetLanguage: String) async -> String`
Translates text to target language.

---

## AppIntegrationManager Class

Manages integration with iOS apps and external services.

### Calendar Methods

#### `createCalendarEvent(title: String, date: Date, duration: TimeInterval) async throws -> Bool`
Creates a calendar event.

**Parameters:**
- `title`: Event title
- `date`: Event start date
- `duration`: Event duration in seconds (default: 3600)

**Returns:** Success status

**Example:**
```swift
let success = try await manager.createCalendarEvent(
    title: "Team Meeting",
    date: Date().addingTimeInterval(86400)
)
```

#### `getUpcomingEvents(days: Int) async throws -> [EKEvent]`
Gets upcoming calendar events.

**Parameters:**
- `days`: Number of days to look ahead (default: 7)

**Returns:** Array of events

### Reminders Methods

#### `createReminder(title: String, dueDate: Date?, notes: String?) async throws -> Bool`
Creates a reminder.

**Parameters:**
- `title`: Reminder title
- `dueDate`: Optional due date
- `notes`: Optional notes

#### `getIncompleteReminders() async throws -> [EKReminder]`
Gets all incomplete reminders.

### Contacts Methods

#### `findContact(name: String) async throws -> CNContact?`
Finds a contact by name.

#### `getAllContacts() async throws -> [CNContact]`
Gets all contacts.

### Real-time Data Methods

#### `fetchWeatherData(location: String) async throws -> WeatherData`
Fetches weather data for a location.

#### `fetchNewsHeadlines() async throws -> [NewsHeadline]`
Fetches latest news headlines.

---

## WorkflowOrchestrator Class

Orchestrates agentic workflows and task execution.

### Methods

#### `executeWorkflow(intent: Intent, context: PersonalizationContext, integrationManager: AppIntegrationManager, modelManager: ModelManager) async throws -> WorkflowResponse`
Executes a workflow based on detected intent.

**Parameters:**
- `intent`: Detected user intent
- `context`: Personalization context
- `integrationManager`: App integration manager instance
- `modelManager`: Model manager instance

**Returns:** Workflow response with message and metadata

---

## Data Models

### ChatMessage

```swift
struct ChatMessage: Identifiable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
    let metadata: String?
}
```

### Intent

```swift
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
```

### UserPreference

```swift
struct UserPreference {
    var preferredLanguage: String
    var preferredCommunicationStyle: String
    var enabledIntegrations: [String]
    var learningData: [String: Any]
}
```

### WorkflowResponse

```swift
struct WorkflowResponse {
    let message: String
    let metadata: String?
    let success: Bool
}
```

---

## Error Handling

### IntegrationError

```swift
enum IntegrationError: Error {
    case notEnabled(String)
    case permissionDenied(String)
    case integrationFailed(String)
}
```

**Usage:**
```swift
do {
    try await manager.createCalendarEvent(title: "Event", date: Date())
} catch IntegrationError.notEnabled(let app) {
    print("Integration not enabled: \(app)")
} catch {
    print("Error: \(error)")
}
```

---

## Best Practices

### 1. Always Handle Errors

```swift
do {
    let response = try await orchestrator.executeWorkflow(...)
    // Handle success
} catch {
    // Handle error appropriately
    print("Workflow failed: \(error)")
}
```

### 2. Use Async/Await Properly

```swift
Task {
    await aiAgent.processCommand(userInput)
}
```

### 3. Check Permissions Before Integration

```swift
await integrationManager.setupIntegrations(enabledApps: ["Calendar", "Reminders"])
```

### 4. Personalize Responses

```swift
let context = PersonalizationContext(
    language: "English",
    communicationStyle: "Conversational",
    userHistory: history,
    learningData: data
)
```

### 5. Monitor Agent Status

```swift
@Published var status: String
// Status values: "Ready", "Processing...", "Error occurred", etc.
```

---

## Performance Tips

1. **Lazy Loading**: Models are loaded on-demand
2. **Caching**: Responses and data are cached where appropriate
3. **Background Processing**: Long operations run asynchronously
4. **Memory Management**: Automatic cleanup of completed workflows
5. **Batch Operations**: Multiple requests can be batched when possible

---

## Version History

### Version 1.0.0
- Initial release
- Multi-model AI support
- App integrations (Calendar, Reminders, Contacts)
- Natural language processing
- Agentic workflows
- User personalization
