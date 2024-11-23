# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import requests
# import time
# import webbrowser

# # --- Configuration ---
# CLIENT_ID = "b3899e28c54a4dc5af8c09e2256bd9e3"  # Replace with your actual Client ID
# CLIENT_SECRET = "ee992ed34c7042918325c0158cffe80d"  # Replace with your actual Client Secret
# REDIRECT_URI = "http://localhost:8888/callback"
# SCOPE = "user-read-recently-played user-top-read user-follow-read playlist-read-private playlist-read-collaborative"  # Permissions you need

# # --- Authentication ---
# def authenticate_spotify():
#     sp_oauth = SpotifyOAuth(
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         redirect_uri=REDIRECT_URI,
#         scope=SCOPE,
#     )

#     auth_url = sp_oauth.get_authorize_url()
#     webbrowser.open(auth_url)

#     print("Please login to Spotify and paste the URL you are redirected to here:")
#     redirected_url = input()

#     code = sp_oauth.parse_response_code(redirected_url)
#     token_info = sp_oauth.get_access_token(code)

#     return spotipy.Spotify(auth=token_info["access_token"])

# # --- Fetch Recent Music and Discoveries ---
# def get_recent_and_interesting_music(sp):
#     # 1. Get recently played tracks
#     try:
#         recent_tracks = sp.current_user_recently_played(limit=20)  # Get the last 20 tracks
#         print("\n--- Recently Played Tracks ---")
        # for track in recent_tracks["items"]:
        #     track_name = track["track"]["name"]
        #     artist_name = track["track"]["artists"][0]["name"]
        #     played_at = track["played_at"]
#             print(f"- {track_name} by {artist_name} (Played at: {played_at})")
#     except Exception as e:
#         print(f"Error getting recently played tracks: {e}")
#         recent_tracks = None

#     # 2. Get top tracks (short-term, medium-term, long-term)
#     try:
#         print("\n--- Top Tracks ---")
#         for term in ["short_term", "medium_term", "long_term"]:
#             top_tracks = sp.current_user_top_tracks(limit=10, time_range=term)
#             print(f"\n-- Top Tracks ({term}):")
#             for i, track in enumerate(top_tracks["items"]):
#                 print(
#                     f"   {i + 1}. {track['name']} by {track['artists'][0]['name']}"
#                 )
#     except Exception as e:
#         print(f"Error getting top tracks: {e}")
#         top_tracks = None

#     # 3. Get artists you follow and check for new releases (simplified)
#     try:
#         followed_artists = sp.current_user_followed_artists(limit=20)
#         print("\n--- New Releases from Followed Artists (Simplified) ---")
#         for artist in followed_artists["artists"]["items"]:
#             artist_id = artist["id"]
#             artist_name = artist["name"]

#             # This is a simplified way; a more robust method would involve checking each artist's albums endpoint
#             albums = sp.artist_albums(artist_id, album_type="album", limit=5)
#             for album in albums["items"]:
#                 print(f"- {artist_name}: {album['name']} ({album['release_date']})")
#     except Exception as e:
#         print(f"Error getting followed artists/new releases: {e}")
#         followed_artists = None

#     # 4.   Recommendations based on recent tracks (if recent data exists)
#     if recent_tracks:
#       try:
#           if recent_tracks["items"]:  # Check if there are any recent tracks
#               seed_tracks = [
#                   track["track"]["id"] for track in recent_tracks["items"][:5]
#               ]  # Use 5 most recent tracks as seeds
#               recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=10)
#               print("\n--- Recommendations Based on Recent Tracks ---")
#               for track in recommendations["tracks"]:
#                   print(
#                       f"- {track['name']} by {track['artists'][0]['name']}"
#                   )
#           else:
#               print(
#                   "\nNo recent tracks found, skipping recommendations based on recent tracks."
#               )
#       except Exception as e:
#           print(f"Error getting track recommendations: {e}")
#           recommendations = None

# # --- Main Execution ---
# if __name__ == "__main__":
#     sp = authenticate_spotify()
#     if sp:
#         get_recent_and_interesting_music(sp)
#     else:
#         print("Authentication failed.")



import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse
import os
import json

# --- Configuration ---
CLIENT_ID = "b3899e28c54a4dc5af8c09e2256bd9e3"  # Replace with your actual Client ID
CLIENT_SECRET = "ee992ed34c7042918325c0158cffe80d"  # Replace with your actual Client Secret
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-read-recently-played user-top-read user-follow-read playlist-read-private playlist-read-collaborative"  # Permissions you need
TOKEN_CACHE_PATH = "spotify_token_cache.json"  # Path to store the token cache

# --- Local Server for Handling Redirect ---
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query_params:
                code = query_params['code'][0]
                self.server.auth_code = code
                self.wfile.write(b"<html><body>You are now logged in. You can close this window.</body></html>")
            else:
                self.wfile.write(b"<html><body>Authorization failed.</body></html>")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body>Not Found.</body></html>")

def run_local_server(server):
    server.serve_forever()

# --- Token Cache Management ---
def load_token_cache():
    try:
        with open(TOKEN_CACHE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_token_cache(token_info):
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(token_info, f)

# --- Authentication ---
def authenticate_spotify():
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )

    # Try to load token cache first
    token_info = load_token_cache()

    if token_info:
        # Check if token is expired
        if sp_oauth.is_token_expired(token_info):
            print("Token expired, refreshing...")
            try:
                token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
                save_token_cache(token_info)
                print("Token refreshed successfully.")
                return spotipy.Spotify(auth=token_info["access_token"])
            except Exception as e:
                print(f"Error refreshing token: {e}")
                token_info = None  # Invalidate token if refresh fails

        if token_info:
            print("Using cached token.")
            return spotipy.Spotify(auth=token_info["access_token"])

    # If no valid cached token, perform full authentication flow
    print("No valid cached token found. Performing full authentication.")
    auth_url = sp_oauth.get_authorize_url()
    webbrowser.open(auth_url)

    server = HTTPServer(('localhost', 8888), RequestHandler)
    server.auth_code = None

    server_thread = threading.Thread(target=run_local_server, args=(server,))
    server_thread.daemon = True
    server_thread.start()

    print("Waiting for authorization in browser...")
    while server.auth_code is None:
        time.sleep(0.1)

    server.shutdown()

    token_info = sp_oauth.get_access_token(server.auth_code)
    save_token_cache(token_info)
    print("Authentication successful and token cached.")
    return spotipy.Spotify(auth=token_info["access_token"])

# --- Fetch Recent Music and Discoveries (same as before) ---
def format_track_info(track):
    """Formats track information with UTF-8 encoding."""
    return f"{track['name']} by {track['artists'][0]['name']}".encode('utf-8').decode('utf-8')

def create_track_json(track, played_at=None, source="Spotify"):
    summary_str = f"Artist: {track['artists'][0]['name']}, Album: {track['album']['name']}".encode('utf-8').decode('utf-8')
    if played_at:
        summary_str += f", Played at: {played_at}"

    track_json = {
        "title": format_track_info(track),
        "link": track["external_urls"].get("spotify"),
        "summary": summary_str,
        "source": source,
        "date": played_at or track["album"]["release_date"]
    }
    return track_json

# --- Data Fetching Methods ---
def get_recent_tracks(sp, limit=20):
    """Fetches recently played tracks as JSON with string summary and played_at date."""
    try:
        recent_tracks_data = sp.current_user_recently_played(limit=limit)
        return [
            create_track_json(item["track"], played_at=item["played_at"]) for item in recent_tracks_data["items"]
        ]  # Pass played_at to create_track_json
    except Exception as e:
        print(f"Error getting recently played tracks: {e}")
        return None

def get_top_tracks(sp, limit=10):
    """Fetches top tracks for different time ranges as JSON."""
    top_tracks_all = []
    try:
        for term in ["short_term", "medium_term", "long_term"]:
            top_tracks_data = sp.current_user_top_tracks(limit=limit, time_range=term)
            for track in top_tracks_data["items"]:
                top_tracks_all.append(create_track_json(track))  # Add time_range to summary if needed
    except Exception as e:
        print(f"Error getting top tracks: {e}")

    return top_tracks_all



def get_followed_artists_and_releases(sp, limit=20, album_limit=1):
    """Fetches followed artists and their recent releases as JSON objects."""
    album_data = []
    try:
        followed_artists = sp.current_user_followed_artists(limit=limit)
        for artist in followed_artists["artists"]["items"]:
            artist_name = artist["name"]
            artist_id = artist["id"]
            albums = sp.artist_albums(artist_id, album_type="album", limit=album_limit)
            for album in albums["items"]:
                album_json = {
                    "title": f"New Album: {album['name']} By {artist_name}".encode('utf-8').decode('utf-8'),
                    "link": album["external_urls"].get("spotify"),
                    "summary": f"New Album: {album['name']} By {artist_name}".encode('utf-8').decode('utf-8'),
                    "date": album['release_date'],
                    "source": "Spotify"
                }
                album_data.append(album_json)
        return album_data

    except Exception as e:
        print(f"Error getting followed artists/new releases: {e}")
        return None

# def get_recommendations_from_recent(sp, recent_tracks, limit=10):
#     """Fetches recommendations based on recent tracks."""
#     if not recent_tracks or not recent_tracks["items"]:  # Check if recent_tracks and items exist
#       print("No recent tracks data available.")
#       return

#     try:
#         seed_tracks = []
#         for item in recent_tracks["items"][:5]:  # Iterate through 'items'
#             seed_tracks.append(item["track"]["id"])

#         recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=limit)
#         print("\n--- Recommendations Based on Recent Tracks ---")
#         for track in recommendations["tracks"]:
#             print(f"- {track['name']} by {track['artists'][0]['name']}")

#     except Exception as e:
#         print(f"Error getting track recommendations: {e}")

# def get_recommendations_from_recent(sp, recent_tracks, limit=10):
#     """Fetches recommendations based on recent tracks."""
#     if not recent_tracks:
#       return None

#     try:
#         if recent_tracks:
#             seed_tracks = [track["track"]["id"] for track in recent_tracks[:5]]  # Use 5 most recent tracks
#             recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=limit)
#             return recommendations["tracks"]
#         else:
#            print("\nNo recent tracks found, skipping recommendations based on recent tracks.")
#            return None
#     except Exception as e:
#         print(f"Error getting track recommendations: {e}")
#         return None


# --- Display Method ---
def display_music_data(music_data):
    if music_data:
        print(json.dumps(music_data, indent=4, ensure_ascii=False))




# --- Main Aggregated Function ---
def get_recent_and_interesting_music():
    sp = authenticate_spotify()
    """Fetches and displays recent and interesting music as JSON."""
    all_music = []
    recent_tracks = get_recent_tracks(sp)

    if recent_tracks:
      all_music.extend(recent_tracks)  # Add recent tracks JSON

    # top_tracks = get_top_tracks(sp)

    # if top_tracks:
    #     all_music.extend(top_tracks)  # Add top tracks JSON

    followed_artists_releases = get_followed_artists_and_releases(sp)
    if followed_artists_releases:
        all_music.extend(followed_artists_releases)

    #recommendations = get_recommendations_from_recent(sp, recent_tracks if recent_tracks else [])
    # if recommendations:
    #    all_music.extend(recommendations)

    #display_music_data(all_music) # Display the final JSON list
    return recent_tracks



# --- Main Execution ---
if __name__ == "__main__":
    sp = authenticate_spotify()
    if sp:
        get_recent_and_interesting_music(sp)

    else:
        print("Authentication failed.")