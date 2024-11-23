import Foundation

struct Model: Identifiable {
    var id = UUID()
    var name: String
    var url: String
    var filename: String
    var status: String?
}

@MainActor
class LlamaState: ObservableObject {
    @Published var messageLog = ""
    @Published var cacheCleared = false
    @Published var downloadedModels: [Model] = []
    @Published var undownloadedModels: [Model] = []
    let NS_PER_S = 1_000_000_000.0

    private var llamaContext: LlamaContext?
    private var defaultModelUrl: URL? {
        Bundle.main.url(forResource: "llama-3.2-1b-instruct-q8_0", withExtension: "gguf", subdirectory: "models")
    }
    
    private let temperature = 0.7 // Add temperature for response variability
    
    // System prompt to better control the model's behavior
    private let systemPrompt = """
    <|system|>You are a helpful AI assistant. Provide direct, concise answers.
    Format: Only provide the answer, no explanations or additional context.</s>
    <|user|>
    """

    init() {
        loadModelsFromDisk()
        loadDefaultModel()
    }
    
    private func loadModelsFromDisk() {
        do {
            let documentsURL = getDocumentsDirectory()
            let modelURLs = try FileManager.default.contentsOfDirectory(at: documentsURL, includingPropertiesForKeys: nil, options: [.skipsHiddenFiles, .skipsSubdirectoryDescendants])
            for modelURL in modelURLs {
                let modelName = modelURL.deletingPathExtension().lastPathComponent
                downloadedModels.append(Model(name: modelName, url: "", filename: modelURL.lastPathComponent, status: "downloaded"))
            }
        } catch {
            print("Error loading models from disk: \(error)")
        }
    }

    private func loadDefaultModel() {
        do {
            if let defaultModelUrl = defaultModelUrl {
                try loadModel(modelUrl: defaultModelUrl)
            } else {
                messageLog += "Default model not found in the models folder.\n"
            }
        } catch {
            messageLog += "Error loading default model: \(error)\n"
        }
    }

    func getDocumentsDirectory() -> URL {
        let paths = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        return paths[0]
    }
    private let defaultModels: [Model] = [
        Model(name: "bartowski/Llama-3.2-3B-Instruct-uncensored-GGUF (Q5_0, 2.6 GiB)",url: "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-uncensored-GGUF/resolve/main/Llama-3.2-3B-Instruct-uncensored-Q5_K_M.gguf?download=true",filename: "Llama-3.2-3B-Instruct-uncensored-Q5_K_M.gguf", status: "download"),
    ]
    func loadModel(modelUrl: URL?) throws {
        if let modelUrl {
            llamaContext = try LlamaContext.create_context(path: modelUrl.path())

            // Assuming that the model is successfully loaded, update the downloaded models
            updateDownloadedModels(modelName: modelUrl.lastPathComponent, status: "downloaded")
        } else {
            messageLog += "Load a model from the list below\n"
        }
    }


    private func updateDownloadedModels(modelName: String, status: String) {
        undownloadedModels.removeAll { $0.name == modelName }
    }


    // Response marker to help separate model's response
    private let responseMarker = "<|assistant|>"
    
    func complete(text: String) async -> String {
        guard let llamaContext else {
            return ""
        }

        var generatedText = ""
        // Construct a better formatted prompt
        let fullPrompt = "\(systemPrompt)\(text)\n\(responseMarker)"
        
        // Initialize completion with the full prompt
        await llamaContext.completion_init(text: fullPrompt)
        
        // Log only the user's input
        messageLog += "\nAssistant: "
        
        while await !llamaContext.is_done {
            let result = await llamaContext.completion_loop()
            
            // Check if the result is not just echoing the prompt
            if !fullPrompt.contains(result) {
                generatedText += result
                await MainActor.run {
                    self.messageLog += result
                }
            }
            
            // Stop if we detect an end of response marker
            if result.contains("</s>") || result.contains("<|end|>") {
                break
            }
        }
        
        await llamaContext.clear()
        loadDefaultModel()
        return generatedText + "\n"
    }

    func bench() async {
        guard let llamaContext else {
            return
        }

        messageLog += "\n"
        messageLog += "Running benchmark...\n"
        messageLog += "Model info: "
        messageLog += await llamaContext.model_info() + "\n"

        let t_start = DispatchTime.now().uptimeNanoseconds
        let _ = await llamaContext.bench(pp: 8, tg: 4, pl: 1) // heat up
        let t_end = DispatchTime.now().uptimeNanoseconds

        let t_heat = Double(t_end - t_start) / NS_PER_S
        messageLog += "Heat up time: \(t_heat) seconds, please wait...\n"

        // if more than 5 seconds, then we're probably running on a slow device
        if t_heat > 5.0 {
            messageLog += "Heat up time is too long, aborting benchmark\n"
            return
        }

        let result = await llamaContext.bench(pp: 512, tg: 128, pl: 1, nr: 3)

        messageLog += "\(result)"
        messageLog += "\n"
    }

    func clear() async {
        guard let llamaContext else {
            return
        }

        await llamaContext.clear()
        messageLog = ""
    }
}
