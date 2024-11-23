import Foundation

// Matches your ContentEntity
struct Content: Codable, Identifiable {
    let id: Int
    let title: String
    let link: String
    let summary: String
    let source: String
    let date: String
    
    // Optional properties that might be added from AI workflow
    var ranking: Int?
    var relevance: Double?
}

// For the workflow endpoint
struct InputUser: Codable {
    let input: String
}

struct WorkflowResponse: Codable {
    let status: String
    let result: String
}
