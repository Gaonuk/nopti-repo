import SwiftUI

struct NowPlayingWidget: View {
    let currentTrack: SpotifyDataManager.TrackInfo?
    
    var body: some View {
        HStack(spacing: 12) {
            if let url = currentTrack?.albumArtURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                    default:
                        Color.gray
                    }
                }
                .frame(width: 60, height: 60)
                .cornerRadius(8)
            } else {
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray)
                    .frame(width: 60, height: 60)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(currentTrack?.title ?? "Not Playing")
                    .font(.system(size: 16, weight: .semibold))
                    .lineLimit(1)
                
                Text(currentTrack?.artist ?? "No Artist")
                    .font(.system(size: 14))
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 5)
    }
}

struct NowPlayingWidget_Previews: PreviewProvider {
    static var previews: some View {
        NowPlayingWidget(currentTrack: SpotifyDataManager.TrackInfo(
            title: "Sample Song",
            artist: "Sample Artist",
            albumArtURL: URL(string: "https://example.com/album_art.jpg")
        ))
        .previewLayout(.sizeThatFits)
    }
}

// End of file. No additional code.
