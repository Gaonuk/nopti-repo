import Foundation
import AVFoundation

enum NetworkError: Error {
    case invalidURL
    case noData
    case decodingError
    case serverError(String)
    case audioPlaybackError(String)
}

class NetworkManager {
    static let shared = NetworkManager()
    private let baseURL = "https://5646-84-14-112-188.ngrok-free.app"
    private var audioPlayer: AVAudioPlayer?
    
    private init() {}
    
    // Fetch content
    func fetchContent() async throws -> [Content] {
        guard let url = URL(string: "\(baseURL)/content") else {
            throw NetworkError.invalidURL
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError("Failed to fetch content")
        }
        
        return try JSONDecoder().decode([Content].self, from: data)
    }
    
    // AI Workflow
    func executeWorkflow(input: String) async throws -> WorkflowResponse {
        guard let url = URL(string: "\(baseURL)/workflow") else {
            throw NetworkError.invalidURL
        }
        
        let inputUser = InputUser(input: input)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(inputUser)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError("Workflow failed")
        }
        
        return try JSONDecoder().decode(WorkflowResponse.self, from: data)
    }
    
    // Reset content
    func resetContent() async throws {
        guard let url = URL(string: "\(baseURL)/reset") else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError("Reset failed")
        }
    }
    
    private let userInputs = ["summarize","next", "play"]
    private var currentInputIndex = 0

    
    func getDecision(userInput: String) async throws -> DecisionResponse {
        let hardcodedInput = userInputs[currentInputIndex]

        currentInputIndex = (currentInputIndex + 1) % userInputs.count

        let urlString = "\(baseURL)/get-decision?user_input=\(hardcodedInput.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"

        guard let url = URL(string: urlString) else {
             throw NetworkError.invalidURL
         }
         
         let (data, response) = try await URLSession.shared.data(from: url)
         
         guard let httpResponse = response as? HTTPURLResponse,
               (200...299).contains(httpResponse.statusCode) else {
             throw NetworkError.serverError("Failed to get decision")
         }
         
         if httpResponse.mimeType == "audio/mpeg" {
//             return DecisionResponse(audio: data)
             Task {
                 try await NetworkManager.shared.playAudio(url: url)
             }
//             try await MainActor.run {
//                 try NetworkManager.shared.playAudio(data: data)
//             }
         }
         
         do {
             let jsonResponse = try JSONDecoder().decode([String: String].self, from: data)
             return DecisionResponse(audio: nil)
         } catch {
             throw NetworkError.decodingError
         }
     }
    
    // Add new function for GET /hello
    func getHello() async throws -> Data {
        guard let url = URL(string: "\(baseURL)/hello") else {
            throw NetworkError.invalidURL
        }
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.serverError("Failed to fetch hello audio")
        }
        
        // Add debugging information
        print("Content-Type: \(httpResponse.mimeType ?? "Unknown")")
        print("Content-Length: \(httpResponse.expectedContentLength)")
        print("Received data size: \(data.count) bytes")
        
        return data
    }
    
    // Add new function for playing audio
    func playAudio(data: Data) throws {
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
            
            audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer?.prepareToPlay()
            
            // Add debugging information
            print("Audio duration: \(audioPlayer?.duration ?? 0) seconds")
            print("Audio format: \(audioPlayer?.format.description ?? "Unknown")")
            
            audioPlayer?.play()
        } catch {
            throw NetworkError.audioPlaybackError(error.localizedDescription)
        }
    }
    
    func playAudio(url: URL) async throws {
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer?.play()
        }
    }
}

struct DecisionResponse {
    let audio: Data?
//    let action: String?
}
