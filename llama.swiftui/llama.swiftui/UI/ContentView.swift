import SwiftUI
import AVFoundation
import Speech

struct ContentView: View {
    @StateObject var llamaState = LlamaState()
    @State private var isListening = false
    @State private var recognizedText = ""
     
    @State private var audioPlayer: AVAudioPlayer?
    
    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var recognitionTask: SFSpeechRecognitionTask?
    @State private var audioEngine = AVAudioEngine()
    @State private var isLoading = true
    
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))!
    
    @State private var isRecording = false
    @State private var scale: CGFloat = 1.0
    
    @State private var errorMessage: String? = nil
    
    @State private var recognizedWords: [String] = []
    
    var body: some View {
        ZStack {
            if isLoading {
                LoaderView()
            } else {
                ZStack {
                    Color.white.edgesIgnoringSafeArea(.all)
                    VStack {
                        ZStack {
                            Circle()
                                .fill(Color.black)
                                .frame(width: 200, height: 200)
                                .scaleEffect(scale)
                                .animation(isRecording ? Animation.easeInOut(duration: 1).repeatForever(autoreverses: true) : .default, value: scale)
                                .onTapGesture {
                                    if isRecording {
                                        stopListening()
                                    } else {
                                        startListening()
                                    }
                                    isRecording.toggle()
                                    scale = isRecording ? 1.1 : 1.0
                                }
                            
                            Text("Hello!")
                                .foregroundColor(.white)
                                .font(.title)
                        }
                        
                        Text(recognizedWords.joined(separator: " "))
                            .padding()
                            .fixedSize(horizontal: false, vertical: true)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .foregroundColor(.black)
                    }
                    
                    VStack {
                        Spacer()
//                        HStack {
//                            Button("Hello") {
//                                Task {
//                                    await playInitialMessage()
//                                }
//                            }
//                            Button("Get Decision") {
//                                Task {
//                                    await getDecision()
//                                }
//                            }
//                            Button("Fetch Content") {
//                                Task {
//                                    await playContent()
//                                }
//                            }
//                        }
//                        .padding()
                        SpotifyView()
                        
                        if let errorMessage = errorMessage {
                            Text(errorMessage)
                                .foregroundColor(.red)
                                .padding()
                        }
                    }
                }
            }
            
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                isLoading = false
                Task {
                    await playInitialMessage()
                }
            }
        }
    }
    
    func playInitialMessage() async {
        do {
            guard let url = URL(string: "https://5646-84-14-112-188.ngrok-free.app/hello") else {
                print("Invalid URL")
                return
            }
            let (data, _) = try await URLSession.shared.data(from: url)
            audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer?.play()
            llamaState.messageLog += "AI: Welcome! How can I assist you today?\n"
            
            while audioPlayer?.isPlaying == true {
                try await Task.sleep(nanoseconds: 100_000_000)
            }
            
            await playContent()
        } catch {
            print("Error playing audio: \(error)")
        }
    }
    
    func playContent() async {
        do {
            guard let url = URL(string: "https://5646-84-14-112-188.ngrok-free.app/content") else {
                print("Invalid URL")
                return
            }
            let (data, _) = try await URLSession.shared.data(from: url)
            audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer?.play()
        } catch {
            print("Error playing audio: \(error)")
        }
    }
    
    func startListening() {
        isListening = true
        recognizedText = ""
        
        SFSpeechRecognizer.requestAuthorization { authStatus in
            DispatchQueue.main.async {
                if authStatus == .authorized {
                    do {
                        try self.startRecording()
                    } catch {
                        print("Failed to start recording: \(error)")
                    }
                } else {
                    print("Speech recognition authorization denied")
                }
            }
        }
    }
    
    func stopListening() {
        if audioEngine.isRunning {
            audioEngine.stop()
            recognitionRequest?.endAudio()
        }
        
        isListening = false
        processVoiceInput(recognizedText)
    }
    
    func processVoiceInput(_ input: String) {
        llamaState.messageLog += "\nUser: \(input)"
        Task {
            let response = await llamaState.complete(text: input)
            playAudio(url: URL(string: "https://filesamples.com/samples/audio/m4a/sample3.m4a"))
        }
    }
    
    func playAudio(fileName: String? = nil, url: URL? = nil, data: Data? = nil) {
        do {
            if let data = data {
                audioPlayer = try AVAudioPlayer(data: data)
            } else if let url = url {
                audioPlayer = try AVAudioPlayer(contentsOf: url)
            } else if let fileName = fileName,
                      let audioURL = Bundle.main.url(forResource: fileName, withExtension: "m4a", subdirectory: "audio") {
                audioPlayer = try AVAudioPlayer(contentsOf: audioURL)
            } else {
                print("Audio file not found")
                return
            }
            
            audioPlayer?.play()
        } catch {
            print("Error playing audio: \(error)")
        }
    }
    
    private func startRecording() throws {
        recognitionTask?.cancel()
        recognitionTask = nil
        
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        
        let inputNode = audioEngine.inputNode
        guard let recognitionRequest = recognitionRequest else { fatalError("Unable to create a SFSpeechAudioBufferRecognitionRequest object") }
        recognitionRequest.shouldReportPartialResults = true
        
        recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { result, error in
            var isFinal = false
            
            if let result = result {
                self.recognizedText = result.bestTranscription.formattedString
                self.recognizedWords = result.bestTranscription.segments.map { $0.substring }
                isFinal = result.isFinal
            }
            
            if error != nil || isFinal {
                self.audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                self.recognitionRequest = nil
                self.recognitionTask = nil
            }
        }
        
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { (buffer: AVAudioPCMBuffer, when: AVAudioTime) in
            self.recognitionRequest?.append(buffer)
        }
        
        audioEngine.prepare()
        try audioEngine.start()
    }
    
    func fetchHello() async {
        do {
            let audioData = try await NetworkManager.shared.getHello()
            try await MainActor.run {
                try NetworkManager.shared.playAudio(data: audioData)
            }
        } catch {
            await MainActor.run {
                if case let NetworkError.audioPlaybackError(message) = error {
                    errorMessage = "Audio playback error: \(message)"
                } else {
                    errorMessage = "Error: \(error.localizedDescription)"
                }
                print("Error details: \(error)")
            }
        }
    }

    func getDecision() async {
        do {
            let decision = try await NetworkManager.shared.getDecision(userInput: "Test input")
            await MainActor.run {
                if let audioData = decision.audio {
                    playAudio(data: audioData)
                } else if let action = decision.action {
                    print("Decision action: \(action)")
                }
            }
        } catch {
            print("Error getting decision: \(error)")
        }
    }

    func fetchContent() async {
        do {
            let content = try await NetworkManager.shared.fetchContent()
            await MainActor.run {
                print("Fetched \(content.count) content items")
            }
        } catch {
            print("Error fetching content: \(error)")
        }
    }
}

struct DrawerView: View {

    @ObservedObject var llamaState: LlamaState
    @State private var showingHelp = false
    func delete(at offsets: IndexSet) {
        offsets.forEach { offset in
            let model = llamaState.downloadedModels[offset]
            let fileURL = getDocumentsDirectory().appendingPathComponent(model.filename)
            do {
                try FileManager.default.removeItem(at: fileURL)
            } catch {
                print("Error deleting file: \(error)")
            }
        }

        llamaState.downloadedModels.remove(atOffsets: offsets)
    }

    func getDocumentsDirectory() -> URL {
        let paths = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        return paths[0]
    }
    var body: some View {
        List {
            Section(header: Text("Download Models From Hugging Face")) {
                HStack {
                    InputButton(llamaState: llamaState)
                }
            }
            Section(header: Text("Downloaded Models")) {
                ForEach(llamaState.downloadedModels) { model in
                    DownloadButton(llamaState: llamaState, modelName: model.name, modelUrl: model.url, filename: model.filename)
                }
                .onDelete(perform: delete)
            }
            Section(header: Text("Default Models")) {
                ForEach(llamaState.undownloadedModels) { model in
                    DownloadButton(llamaState: llamaState, modelName: model.name, modelUrl: model.url, filename: model.filename)
                }
            }
        }
        .listStyle(GroupedListStyle())
        .navigationBarTitle("Model Settings", displayMode: .inline).toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Help") {
                    showingHelp = true
                }
            }
        }.sheet(isPresented: $showingHelp) {
            VStack(alignment: .leading) {
                VStack(alignment: .leading) {
                    Text("1. Make sure the model is in GGUF Format")
                            .padding()
                    Text("2. Copy the download link of the quantized model")
                            .padding()
                }
                Spacer()
               }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
