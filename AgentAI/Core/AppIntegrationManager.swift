//
//  AppIntegrationManager.swift
//  AgentAI
//
//  Manages integration with iOS apps (Calendar, Reminders, Messages, etc.)
//

import Foundation
import EventKit
import Contacts
import CoreLocation

class AppIntegrationManager {
    
    // MARK: - Properties
    private let eventStore = EKEventStore()
    private let contactStore = CNContactStore()
    private var enabledIntegrations: Set<String> = []
    
    // MARK: - Initialization
    init() {
        setupDefaultIntegrations()
    }
    
    // MARK: - Public Methods
    
    /// Setup integrations with specified apps
    func setupIntegrations(enabledApps: [String]) async {
        for app in enabledApps {
            enabledIntegrations.insert(app)
        }
        
        // Request necessary permissions
        await requestPermissions()
    }
    
    // MARK: - Calendar Integration
    
    /// Create a calendar event
    func createCalendarEvent(title: String, date: Date, duration: TimeInterval = 3600) async throws -> Bool {
        guard enabledIntegrations.contains("Calendar") else {
            throw IntegrationError.notEnabled("Calendar")
        }
        
        let event = EKEvent(eventStore: eventStore)
        event.title = title
        event.startDate = date
        event.endDate = date.addingTimeInterval(duration)
        event.calendar = eventStore.defaultCalendarForNewEvents
        
        try eventStore.save(event, span: .thisEvent)
        return true
    }
    
    /// Get upcoming events
    func getUpcomingEvents(days: Int = 7) async throws -> [EKEvent] {
        guard enabledIntegrations.contains("Calendar") else {
            throw IntegrationError.notEnabled("Calendar")
        }
        
        let startDate = Date()
        let endDate = Calendar.current.date(byAdding: .day, value: days, to: startDate)!
        
        let predicate = eventStore.predicateForEvents(withStart: startDate, end: endDate, calendars: nil)
        let events = eventStore.events(matching: predicate)
        
        return events
    }
    
    // MARK: - Reminders Integration
    
    /// Create a reminder
    func createReminder(title: String, dueDate: Date? = nil, notes: String? = nil) async throws -> Bool {
        guard enabledIntegrations.contains("Reminders") else {
            throw IntegrationError.notEnabled("Reminders")
        }
        
        let reminder = EKReminder(eventStore: eventStore)
        reminder.title = title
        reminder.calendar = eventStore.defaultCalendarForNewReminders()
        
        if let dueDate = dueDate {
            let dueDateComponents = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: dueDate)
            reminder.dueDateComponents = dueDateComponents
        }
        
        if let notes = notes {
            reminder.notes = notes
        }
        
        try eventStore.save(reminder, commit: true)
        return true
    }
    
    /// Get incomplete reminders
    func getIncompleteReminders() async throws -> [EKReminder] {
        guard enabledIntegrations.contains("Reminders") else {
            throw IntegrationError.notEnabled("Reminders")
        }
        
        return try await withCheckedThrowingContinuation { continuation in
            let predicate = eventStore.predicateForIncompleteReminders(
                withDueDateStarting: nil,
                ending: nil,
                calendars: nil
            )
            
            eventStore.fetchReminders(matching: predicate) { reminders in
                if let reminders = reminders {
                    continuation.resume(returning: reminders)
                } else {
                    continuation.resume(returning: [])
                }
            }
        }
    }
    
    // MARK: - Contacts Integration
    
    /// Find contact by name
    func findContact(name: String) async throws -> CNContact? {
        guard enabledIntegrations.contains("Contacts") else {
            throw IntegrationError.notEnabled("Contacts")
        }
        
        let keysToFetch = [
            CNContactGivenNameKey,
            CNContactFamilyNameKey,
            CNContactPhoneNumbersKey,
            CNContactEmailAddressesKey
        ] as [CNKeyDescriptor]
        
        let predicate = CNContact.predicateForContacts(matchingName: name)
        let contacts = try contactStore.unifiedContacts(matching: predicate, keysToFetch: keysToFetch)
        
        return contacts.first
    }
    
    /// Get all contacts
    func getAllContacts() async throws -> [CNContact] {
        guard enabledIntegrations.contains("Contacts") else {
            throw IntegrationError.notEnabled("Contacts")
        }
        
        let keysToFetch = [
            CNContactGivenNameKey,
            CNContactFamilyNameKey,
            CNContactPhoneNumbersKey
        ] as [CNKeyDescriptor]
        
        let request = CNContactFetchRequest(keysToFetch: keysToFetch)
        var contacts: [CNContact] = []
        
        try contactStore.enumerateContacts(with: request) { contact, _ in
            contacts.append(contact)
        }
        
        return contacts
    }
    
    // MARK: - Real-time Data Integration
    
    /// Fetch weather data (simulated - would integrate with weather API)
    func fetchWeatherData(location: String) async throws -> WeatherData {
        // Simulate API call
        try await Task.sleep(nanoseconds: 500_000_000)
        
        return WeatherData(
            temperature: 72,
            condition: "Sunny",
            location: location
        )
    }
    
    /// Fetch news headlines (simulated - would integrate with news API)
    func fetchNewsHeadlines() async throws -> [NewsHeadline] {
        // Simulate API call
        try await Task.sleep(nanoseconds: 500_000_000)
        
        return [
            NewsHeadline(title: "Latest Technology News", source: "Tech Daily"),
            NewsHeadline(title: "Global Market Update", source: "Finance News")
        ]
    }
    
    // MARK: - Private Methods
    
    private func setupDefaultIntegrations() {
        enabledIntegrations = ["Calendar", "Reminders", "Contacts"]
    }
    
    private func requestPermissions() async {
        // Request Calendar and Reminders access
        if enabledIntegrations.contains("Calendar") || enabledIntegrations.contains("Reminders") {
            do {
                let granted = try await eventStore.requestAccess(to: .event)
                if !granted {
                    print("Calendar access not granted")
                }
                
                let remindersGranted = try await eventStore.requestAccess(to: .reminder)
                if !remindersGranted {
                    print("Reminders access not granted")
                }
            } catch {
                print("Error requesting calendar/reminders access: \(error)")
            }
        }
        
        // Request Contacts access
        if enabledIntegrations.contains("Contacts") {
            do {
                let granted = try await contactStore.requestAccess(for: .contacts)
                if !granted {
                    print("Contacts access not granted")
                }
            } catch {
                print("Error requesting contacts access: \(error)")
            }
        }
    }
}

// MARK: - Supporting Models

enum IntegrationError: Error, LocalizedError {
    case notEnabled(String)
    case permissionDenied(String)
    case integrationFailed(String)
    
    var errorDescription: String? {
        switch self {
        case .notEnabled(let app):
            return "\(app) integration is not enabled"
        case .permissionDenied(let app):
            return "Permission denied for \(app)"
        case .integrationFailed(let reason):
            return "Integration failed: \(reason)"
        }
    }
}

struct WeatherData {
    let temperature: Int
    let condition: String
    let location: String
}

struct NewsHeadline {
    let title: String
    let source: String
}
