# Examples and Use Cases

## Basic Usage Examples

### 1. Simple Greeting

**User Input:**
```
"Hello"
```

**Agent Response:**
```
"Hello! How can I help you today?"
```

**What Happens:**
1. NLPProcessor analyzes intent → `.general`
2. ModelManager generates personalized greeting
3. Response delivered to user

---

### 2. Schedule a Meeting

**User Input:**
```
"Schedule a team meeting tomorrow at 2 PM"
```

**Agent Response:**
```
"Done! Created calendar event: team meeting. Found 3 upcoming events"
```

**Workflow:**
1. Intent detected: `.scheduling`
2. Entities extracted: 
   - title: "team meeting"
   - datetime: tomorrow at 2 PM
3. Calendar event created
4. Upcoming events retrieved
5. Formatted response returned

---

### 3. Create a Reminder

**User Input:**
```
"Remind me to call John tomorrow"
```

**Agent Response:**
```
"✓ Created reminder: call John"
```

**Workflow:**
1. Intent: `.taskManagement`
2. Entities: title="call John", datetime=tomorrow
3. Reminder created in iOS Reminders app
4. Confirmation returned

---

### 4. Weather Query

**User Input:**
```
"What's the weather like?"
```

**Agent Response:**
```
"The weather is Sunny with a temperature of 72°F"
```

**Workflow:**
1. Intent: `.informationRetrieval`
2. Query type: weather
3. Fetch weather data from API
4. Format and return response

---

### 5. Find Contact

**User Input:**
```
"Find contact information for Sarah"
```

**Agent Response:**
```
"Found contact: Sarah Johnson"
```

**Workflow:**
1. Intent: `.communication`
2. Entity: person="Sarah"
3. Search contacts database
4. Return match

---

## Advanced Use Cases

### Multi-Step Workflow

**User Input:**
```
"Schedule a lunch meeting with Alex tomorrow at noon and send him a reminder"
```

**Workflow Steps:**
1. Find contact "Alex"
2. Create calendar event "lunch meeting" at noon tomorrow
3. Create reminder for the meeting
4. Prepare message draft (if messaging enabled)

**Agent Response:**
```
"Done! I've:
✓ Found contact: Alex Martinez
✓ Created calendar event: lunch meeting
✓ Created reminder for tomorrow at noon"
```

---

### Context-Aware Conversation

**Conversation Flow:**

**User:** "What's on my calendar tomorrow?"

**Agent:** "You have 2 events tomorrow:
1. Team Meeting at 10 AM
2. Lunch with Alex at 12 PM"

**User:** "Cancel the first one"

**Agent:** "I've canceled the Team Meeting scheduled for tomorrow at 10 AM."

**Note:** Agent maintains context from previous messages.

---

### Personalized Responses

**Scenario 1: Formal Style**

**User Preference:** Communication Style = "Formal"

**User:** "What's the weather?"

**Agent:** "The current weather conditions indicate a sunny day with a temperature of 72 degrees Fahrenheit."

**Scenario 2: Conversational Style**

**User Preference:** Communication Style = "Conversational"

**User:** "What's the weather?"

**Agent:** "It's sunny and 72°F! Perfect weather today!"

---

## Real-World Scenarios

### Morning Routine

**User:** "Good morning"

**Agent Workflow:**
1. Greeting based on time of day
2. Check upcoming events
3. Fetch weather
4. Get news headlines

**Agent Response:**
```
"Good morning! Here's your day:
☀️ Weather: Sunny, 68°F
📅 You have 3 events today, starting with Team Standup at 9 AM
📰 Top news: [Headlines...]"
```

---

### Task Planning

**User:** "Help me plan my week"

**Agent Workflow:**
1. Retrieve all events for the week
2. Get incomplete reminders
3. Analyze schedule conflicts
4. Suggest optimal task scheduling

**Agent Response:**
```
"Here's your week overview:
📅 5 scheduled events
✅ 3 pending tasks
💡 Suggestion: You have free time Tuesday afternoon for those pending tasks"
```

---

### Quick Information

**User:** "Tell me about my next meeting"

**Agent Workflow:**
1. Get current time
2. Find next upcoming event
3. Fetch event details
4. Check attendees (if available)

**Agent Response:**
```
"Your next meeting is 'Sprint Planning' at 3 PM today (in 45 minutes)"
```

---

## Integration Examples

### Calendar Integration

```swift
// Create event
try await integrationManager.createCalendarEvent(
    title: "Product Demo",
    date: tomorrowAt2PM,
    duration: 3600
)

// Get events
let events = try await integrationManager.getUpcomingEvents(days: 7)
for event in events {
    print("\(event.title) at \(event.startDate)")
}
```

### Reminders Integration

```swift
// Create reminder with due date
try await integrationManager.createReminder(
    title: "Review PR",
    dueDate: tomorrowAt10AM,
    notes: "Check the new feature implementation"
)

// Get all incomplete reminders
let reminders = try await integrationManager.getIncompleteReminders()
```

### Contacts Integration

```swift
// Find specific contact
if let contact = try await integrationManager.findContact(name: "John Doe") {
    let phone = contact.phoneNumbers.first?.value.stringValue
    print("Phone: \(phone ?? "N/A")")
}
```

---

## Error Handling Examples

### Permission Denied

**User:** "Add an event to my calendar"

**Agent (if permission denied):**
```
"I need access to your calendar to create events. 
Please grant permission in Settings → Privacy → Calendars"
```

### Network Error

**User:** "What's the weather?"

**Agent (if network fails):**
```
"I'm having trouble fetching weather data right now. 
Please check your internet connection and try again."
```

### Ambiguous Input

**User:** "Remind me tomorrow"

**Agent:**
```
"I'd be happy to create a reminder for tomorrow. 
What should I remind you about?"
```

---

## Code Examples

### Custom Workflow

```swift
// Create a custom workflow
let workflow = Workflow(
    id: UUID(),
    type: .taskManagement,
    steps: [
        WorkflowStep(action: .createReminder(
            title: "Buy groceries",
            date: tomorrow
        )),
        WorkflowStep(action: .createReminder(
            title: "Prepare dinner",
            date: tomorrowEvening
        ))
    ],
    context: personalizationContext
)

// Execute workflow
let response = try await orchestrator.executeWorkflow(...)
```

### Custom Intent Processing

```swift
func processCustomIntent(_ text: String) async {
    let intent = await nlpProcessor.analyzeIntent(text)
    
    switch intent.type {
    case .scheduling:
        // Handle scheduling
        await handleScheduling(intent)
    case .taskManagement:
        // Handle task management
        await handleTaskManagement(intent)
    default:
        // Handle other cases
        await handleGeneral(intent)
    }
}
```

---

## Tips for Best Results

### 1. Be Specific
❌ "Remind me later"
✅ "Remind me to call John at 3 PM tomorrow"

### 2. Use Natural Language
✅ "Schedule a meeting next Tuesday at 2"
✅ "What's my schedule looking like tomorrow?"
✅ "Remind me to buy milk when I'm at the store"

### 3. Provide Context
✅ "Find my friend Sarah's phone number"
✅ "Schedule a 30-minute meeting with the engineering team"

### 4. Break Down Complex Tasks
Instead of: "Plan my entire week and optimize my schedule"
Try: 
1. "What's on my calendar this week?"
2. "What tasks do I have pending?"
3. "When do I have free time?"

---

## Performance Considerations

### Response Times
- Simple queries: < 1 second
- Calendar operations: 1-2 seconds
- Complex workflows: 2-5 seconds
- Real-time data fetching: 1-3 seconds

### Resource Usage
- Memory: ~50-100 MB typical
- CPU: Minimal when idle, moderate during processing
- Network: Only for real-time data (weather, news)

### Optimization Tips
1. Cache frequently accessed data
2. Use batch operations when possible
3. Enable offline mode for core features
4. Preload common models

---

## Troubleshooting

### Common Issues

**Issue:** Agent not responding
**Solution:** Check status indicator, restart app if needed

**Issue:** Calendar events not created
**Solution:** Verify calendar permissions in Settings

**Issue:** Slow response times
**Solution:** Check network connection, clear cache

**Issue:** Incorrect intent detection
**Solution:** Rephrase command more clearly, use specific keywords

---

## Future Enhancement Ideas

1. **Voice Control**: "Hey Agent, what's my schedule?"
2. **Proactive Suggestions**: Agent suggests actions based on patterns
3. **Smart Notifications**: Context-aware reminders
4. **Multi-device Sync**: Seamless experience across devices
5. **Third-party Integrations**: Slack, Trello, Gmail, etc.
