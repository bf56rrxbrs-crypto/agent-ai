# Copilot Instructions for agent-ai

## Project Overview
This is an exclusive mobile agent for iPhone focused on delivering seamless, high-performance applications with exceptional design and user experience.

## Technology Stack
- **Primary Languages**: Swift, Objective-C
- **Platform**: iOS (iPhone)
- **Focus**: Mobile application development with emphasis on design and UX

## Coding Standards

### Swift Development
- Follow Swift API Design Guidelines
- Use modern Swift features and syntax (latest stable version)
- Prefer value types (structs) over reference types (classes) when appropriate
- Use protocol-oriented programming where it improves code clarity and reusability
- Implement proper error handling with Result types or throwing functions
- Use optionals appropriately and avoid force unwrapping when possible

### Objective-C Development
- Follow Apple's Objective-C coding conventions
- Use proper naming conventions (camelCase for methods, PascalCase for classes)
- Implement proper memory management patterns
- Use nullability annotations for better Swift interoperability

### Code Quality
- Write clean, self-documenting code with meaningful variable and function names
- Add comments for complex logic, but prefer code clarity over excessive commenting
- Keep functions focused and single-purpose
- Follow DRY (Don't Repeat Yourself) principle
- Ensure code is testable and maintainable

### Architecture & Design Patterns
- Use appropriate iOS design patterns (MVC, MVVM, Coordinator, etc.)
- Follow SOLID principles
- Implement proper separation of concerns
- Use dependency injection for better testability
- Consider performance implications, especially for mobile constraints

### UI/UX Considerations
- Prioritize user experience in all implementations
- Follow Apple Human Interface Guidelines
- Ensure responsive and fluid animations
- Optimize for different screen sizes and orientations
- Consider accessibility features (VoiceOver, Dynamic Type, etc.)
- Test on actual devices when possible

### Performance & Best Practices
- Optimize for mobile performance (battery life, memory usage, network efficiency)
- Use appropriate caching strategies
- Implement proper background task handling
- Follow App Store guidelines and requirements
- Stay current with iOS platform updates and industry trends

## Testing
- Write unit tests for business logic
- Include UI tests for critical user flows
- Test edge cases and error scenarios
- Ensure backward compatibility when supporting multiple iOS versions

## Version Control
- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Follow the project's branching strategy

## Documentation
- Document public APIs and complex implementations
- Keep README and other documentation up to date
- Include setup instructions for new developers
- Document any third-party dependencies and their purposes
