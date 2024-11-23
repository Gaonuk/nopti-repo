import SwiftUI

struct SpotifyView: View {
    var body: some View {
        Button(action: {
            // Action to open Spotify app and play "Never Gonna Give You Up"
            if let url = URL(string: "spotify://track/4cOdK2wGLETKBW3PvgPWqT") {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
            }
        }) {
            Text("Open Spotify")
                .padding()
                .background(Color.green)
                .foregroundColor(.white)
                .cornerRadius(10)
        }
    }
}

struct SpotifyView_Previews: PreviewProvider {
    static var previews: some View {
        SpotifyView()
    }
}

// End of file. No additional code.
