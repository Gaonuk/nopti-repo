import SwiftUI
import UIKit
import SpotifyiOS

class SpotifyPlayerViewController: UIViewController, SPTSessionManagerDelegate, SPTAppRemoteDelegate, SPTAppRemotePlayerStateDelegate {
    
    // Replace 'YOUR_CLIENT_ID' with your actual Spotify Client ID
    private let SpotifyClientID = "24d169d4956e47668e221b997ffd909a"
    private let SpotifyRedirectURL = URL(string: "nopti-spotify://spotify-login-callback")!
    
    // MARK: - Properties
    private var accessToken: String?
    private var sessionManager: SPTSessionManager?
    private var appRemote: SPTAppRemote?
    
    private let playPauseButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Play", for: .normal)
        button.addTarget(SpotifyPlayerViewController.self, action: #selector(playPauseButtonTapped), for: .touchUpInside)
        return button
    }()
    
    private let trackLabel: UILabel = {
        let label = UILabel()
        label.text = "No track playing"
        label.textAlignment = .center
        return label
    }()
    
    // Add this property to store the completion handler
    var onDismiss: (() -> Void)?
    
    // MARK: - Lifecycle Methods
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupSpotify()
        
        // Add a close button
        navigationItem.leftBarButtonItem = UIBarButtonItem(barButtonSystemItem: .close, target: self, action: #selector(dismissViewController))
    }
    
    // MARK: - UI Setup
    private func setupUI() {
        view.backgroundColor = .white
        
        view.addSubview(playPauseButton)
        view.addSubview(trackLabel)
        
        playPauseButton.translatesAutoresizingMaskIntoConstraints = false
        trackLabel.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            playPauseButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            playPauseButton.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            
            trackLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            trackLabel.topAnchor.constraint(equalTo: playPauseButton.bottomAnchor, constant: 20)
        ])
    }
    
    // MARK: - Spotify Setup
    private func setupSpotify() {
        let configuration = SPTConfiguration(clientID: SpotifyClientID, redirectURL: SpotifyRedirectURL)
        sessionManager = SPTSessionManager(configuration: configuration, delegate: self)
        
        appRemote = SPTAppRemote(configuration: configuration, logLevel: .debug)
        appRemote?.delegate = self
    }
    
    // MARK: - Actions
    @objc private func playPauseButtonTapped() {
        if let appRemote = appRemote, appRemote.isConnected {
            appRemote.playerAPI?.getPlayerState { [weak self] (result, error) in
                if let playerState = result as? SPTAppRemotePlayerState {
                    if playerState.isPaused {
                        appRemote.playerAPI?.resume(nil)
                        self?.playPauseButton.setTitle("Pause", for: .normal)
                    } else {
                        appRemote.playerAPI?.pause(nil)
                        self?.playPauseButton.setTitle("Play", for: .normal)
                    }
                }
            }
        } else {
            connect()
        }
    }
    
    // MARK: - Spotify Connection
    private func connect() {
        guard let sessionManager = sessionManager else { return }
        // Update this line to include the 'campaign' parameter
        sessionManager.initiateSession(with: [.streaming], options: .default, campaign: "nopti-spotify")
    }
    
    // MARK: - SPTSessionManagerDelegate
    func sessionManager(manager: SPTSessionManager, didInitiate session: SPTSession) {
        appRemote?.connectionParameters.accessToken = session.accessToken
        appRemote?.connect()
    }
    
    func sessionManager(manager: SPTSessionManager, didFailWith error: Error) {
        print("Failed to initialize session: \(error.localizedDescription)")
    }
    
    // MARK: - SPTAppRemoteDelegate
    func appRemoteDidEstablishConnection(_ appRemote: SPTAppRemote) {
        print("Connected to Spotify")
        appRemote.playerAPI?.delegate = self
        appRemote.playerAPI?.subscribe(toPlayerState: { (result, error) in
            if let error = error {
                print("Error subscribing to player state: \(error.localizedDescription)")
            }
        })
    }
    
    func appRemote(_ appRemote: SPTAppRemote, didDisconnectWithError error: Error?) {
        print("Disconnected from Spotify")
    }
    
    func appRemote(_ appRemote: SPTAppRemote, didFailConnectionAttemptWithError error: Error?) {
        print("Failed to connect to Spotify: \(error?.localizedDescription ?? "Unknown error")")
    }
    
    // MARK: - SPTAppRemotePlayerStateDelegate
    func playerStateDidChange(_ playerState: SPTAppRemotePlayerState) {
        trackLabel.text = playerState.track.name
        playPauseButton.setTitle(playerState.isPaused ? "Play" : "Pause", for: .normal)
    }
    
    // Add this method to dismiss the view controller
    @objc private func dismissViewController() {
        dismiss(animated: true, completion: onDismiss)
    }
}

// Add this extension to create a SwiftUI wrapper for the UIViewController
extension SpotifyPlayerViewController {
    struct SwiftUIView: UIViewControllerRepresentable {
        let onDismiss: () -> Void
        
        func makeUIViewController(context: Context) -> SpotifyPlayerViewController {
            let controller = SpotifyPlayerViewController()
            controller.onDismiss = onDismiss
            return controller
        }
        
        func updateUIViewController(_ uiViewController: SpotifyPlayerViewController, context: Context) {}
    }
}
