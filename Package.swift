// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "AgentAI",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .library(
            name: "AgentAI",
            targets: ["AgentAI"]
        ),
    ],
    dependencies: [
        // Add any external dependencies here
        // .package(url: "https://github.com/example/package.git", from: "1.0.0"),
    ],
    targets: [
        .target(
            name: "AgentAI",
            dependencies: [],
            path: "AgentAI/Core"
        ),
        .testTarget(
            name: "AgentAITests",
            dependencies: ["AgentAI"]
        ),
    ]
)
