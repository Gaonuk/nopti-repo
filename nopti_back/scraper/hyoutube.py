import os
import pickle
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeFeedFetcher:
    def __init__(self, client_secrets_file="credentials/david_youtube_app_secrets.json", token_file="scraper/token.pickle"):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        self.CLIENT_SECRETS_FILE = client_secrets_file
        self.TOKEN_FILE = token_file
        self.credentials = None

    def authenticate(self):
        """Authenticate with the YouTube Data API and get credentials."""
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    os.remove(self.TOKEN_FILE)  # Remove the invalid token
                    self.credentials = None  # Force re-authentication
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)

            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(self.credentials, token)

        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=self.credentials)

    def get_subscriptions_feed(self, max_results=25, order='date', published_after=None, published_before=None):
        """Fetches recent videos from subscribed channels."""
        try:
            youtube = self.authenticate()
            videos = []
            page_token = None

            while True:  # Handle pagination
                request = youtube.subscriptions().list(
                    part="snippet",
                    mine=True,
                    maxResults=min(max_results, 50),  # API max is 50
                    pageToken=page_token
                )
                response = request.execute()

                for item in response['items']:
                    channel_id = item['snippet']['resourceId']['channelId']
                    videos_request = youtube.search().list(
                        part="snippet",
                        channelId=channel_id,
                        maxResults=min(max_results, 50),  # API max is 50
                        order=order,
                        type='video',
                        publishedAfter=published_after,
                        publishedBefore=published_before
                    )
                    videos_response = videos_request.execute()
                    videos.extend(videos_response.get('items', []))
                    if len(videos) >= max_results:
                        break
                if len(videos) >= max_results or 'nextPageToken' not in response:
                    break
                page_token = response['nextPageToken']

            return videos[:max_results]

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_recommended_videos(self, max_results=25):
        """Fetches recommended videos for the authenticated user."""
        try:
            youtube = self.authenticate()
            request = youtube.activities().list(
                part="snippet,contentDetails",
                home=True,
                maxResults=max_results
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_history(self, max_results=25):
        """Fetches the authenticated user's watch history."""
        try:
            youtube = self.authenticate()
            request = youtube.activities().list(
                part='snippet,contentDetails',
                mine=True,
                maxResults=max_results
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def search_videos(self, query, max_results=25, order='relevance', published_after=None, published_before=None):
        """Searches for videos based on a query."""
        try:
            youtube = self.authenticate()
            request = youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_channel_infos(self, channel_id_or_username):
        """Gets infos about a channel using its id or username."""
        try:
            youtube = self.authenticate()
            request = youtube.channels().list(
                part='snippet,statistics,brandingSettings',
                forUsername=channel_id_or_username
            )
            try:
                response = request.execute()
            except HttpError as e:
                if e.resp.status == 400:
                    request = youtube.channels().list(
                        part='snippet,statistics,brandingSettings',
                        id=channel_id_or_username
                    )
                    response = request.execute()
                else:
                    raise e
            return response.get('items', [])
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_playlist_videos(self, playlist_id, max_results=25):
        """Gets videos from a playlist using its id."""
        try:
            youtube = self.authenticate()
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []


def get_youtube_subscription_videos():
    fetcher = YouTubeFeedFetcher()
    subscription_videos = fetcher.get_subscriptions_feed(max_results=100)
    feed_json_list = []
    for video in subscription_videos:
        title = video['snippet']['title']
        description = video['snippet']['description']
        channel_title = video['snippet']['channelTitle']
        video_id = video['id']['videoId'] if 'videoId' in video['id'] else video['id']
        published_at = video['snippet']['publishedAt']
        feed_json_list.append(
            {
                "title": title+". Published by " + channel_title,
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "date": published_at,
                "summary": description,
                "source": "Youtube"
            })
    return feed_json_list

# Usage Example
if __name__ == "__main__":
    #fetcher = YouTubeFeedFetcher()

    print(get_youtube_subscription_videos())


    #Get Subscription Feed
    # print("Fetching subscription feed...")
    # subscription_videos = fetcher.get_subscriptions_feed(max_results=100)
    # if subscription_videos:
    #     for video in subscription_videos:
    #         try:
    #             title = video['snippet']['title']
    #             description = video['snippet']['description']
    #             channel_title = video['snippet']['channelTitle']
    #             video_id = video['id']['videoId'] if 'videoId' in video['id'] else video['id']
    #             published_at = video['snippet']['publishedAt']
    #             print(f"Title: {title}")
    #             print(f"Description: {description}")
    #             print(f"Channel: {channel_title}")
    #             print(f"Video ID: {video_id}")
    #             print(f"Published At: {published_at}")
    #             print(f"URL: https://www.youtube.com/watch?v={video_id}")
    #             print("---")
    #             print(video['snippet'].keys())
    #         except KeyError as e:
    #             print(f"Missing key in video data: {e}")
    #             continue
    # else:
    #     print("No subscription videos found.")

    # Get Recommended Videos
    # print("\nFetching recommended videos...")
    # recommended_videos = fetcher.get_recommended_videos(max_results=5)
    # if recommended_videos:
    #     for video in recommended_videos:
    #         try:
    #             title = video['snippet']['title']
    #             channel_title = video['snippet']['channelTitle']
    #             video_id = video['contentDetails']['upload']['videoId'] if 'upload' in video['contentDetails'] else video['id']
    #             published_at = video['snippet']['publishedAt']
    #             print(f"Title: {title}")
    #             print(f"Channel: {channel_title}")
    #             print(f"Video ID: {video_id}")
    #             print(f"Published At: {published_at}")
    #             print(f"URL: https://www.youtube.com/watch?v={video_id}")
    #             print("---")
    #         except KeyError as e:
    #             print(f"Missing key in video data: {e}")
    #             continue
    # else:
    #     print("No recommended videos found.")

    # Get History
    # print("\nFetching watch history...")
    # history_videos = fetcher.get_history(max_results=5)
    # if history_videos:
    #     for video in history_videos:
    #         try:
    #             #title = video['snippet']['ti']
    #             channel_title = video['snippet']['channelTitle']
    #             video_id = video['contentDetails']['upload']['videoId'] if 'upload' in video['contentDetails'] else video['id']
    #             published_at = video['snippet']['publishedAt']
    #             #print(f"Title: {title}")
    #             print(f"Channel: {channel_title}")
    #             print(f"Video ID: {video_id}")
    #             print(f"Published At: {published_at}")
    #             print(f"URL: https://www.youtube.com/watch?v={video_id}")
    #             print("---")
    #             print(video["contentDetails"].keys())
    #         except KeyError as e:
    #             print(f"Missing key in video data: {e}")
    #             continue
    # else:
    #     print("No watch history found.")

    # Search Videos
    # print("\nSearching for videos...")
    # query = "Python tutorial"
    # searched_videos = fetcher.search_videos(query, max_results=5)
    # if searched_videos:
    #     for video in searched_videos:
    #         try:
    #             title = video['snippet']['title']
    #             channel_title = video['snippet']['channelTitle']
    #             video_id = video['id']['videoId']
    #             published_at = video['snippet']['publishedAt']
    #             print(f"Title: {title}")
    #             print(f"Channel: {channel_title}")
    #             print(f"Video ID: {video_id}")
    #             print(f"Published At: {published_at}")
    #             print(f"URL: https://www.youtube.com/watch?v={video_id}")
    #             print("---")
    #         except KeyError as e:
    #             print(f"Missing key in video data: {e}")
    #             continue
    # else:
    #     print(f"No videos found for '{query}'.")

    # Get Channel Infos
    # print("\nFetching channel infos...")
    # channel_id_or_username = "Google"  # Can be either channel ID or username
    # channel_infos = fetcher.get_channel_infos(channel_id_or_username)
    # if channel_infos:
    #     for channel in channel_infos:
    #         try:
    #             title = channel['snippet']['title']
    #             description = channel['snippet']['description']
    #             custom_url = channel['snippet'].get('customUrl', None)
    #             country = channel['snippet'].get('country', None)
    #             published_at = channel['snippet']['publishedAt']
    #             view_count = channel['statistics']['viewCount']
    #             subscriber_count = channel['statistics']['subscriberCount']
    #             video_count = channel['statistics']['videoCount']
    #             print(f"Title: {title}")
    #             print(f"Description: {description}")
    #             print(f"Custom URL: {custom_url}")
    #             print(f"Country: {country}")
    #             print(f"Published At: {published_at}")
    #             print(f"View Count: {view_count}")
    #             print(f"Subscriber Count: {subscriber_count}")
    #             print(f"Video Count: {video_count}")
    #             print("---")
    #         except KeyError as e:
    #             print(f"Missing key in channel data: {e}")
    #             continue
    # else:
    #     print(f"No channel found for '{channel_id_or_username}'.")

    # Get Playlist Videos
    # print("\nFetching playlist videos...")
    # playlist_id = "PLsyeObzWxF7poL9JTVbP_P2PUGfpP_eUM"  # Example playlist ID
    # playlist_videos = fetcher.get_playlist_videos(playlist_id, max_results=5)
    # if playlist_videos:
    #     for video in playlist_videos:
    #         try:
    #             title = video['snippet']['title']
    #             channel_title = video['snippet']['channelTitle']
    #             video_id = video['snippet']['resourceId']['videoId']
    #             published_at = video['snippet']['publishedAt']
    #             print(f"Title: {title}")
    #             print(f"Channel: {channel_title}")
    #             print(f"Video ID: {video_id}")
    #             print(f"Published At: {published_at}")
    #             print(f"URL: https://www.youtube.com/watch?v={video_id}")
    #             print("---")
    #         except KeyError as e:
    #             print(f"Missing key in video data: {e}")
    #             continue
    # else:
    #     print(f"No videos found for playlist '{playlist_id}'.")

    # Example with date filtering
    # print("\nFetching subscription feed with date filtering...")
    # today = datetime.date.today()
    # last_week = today - datetime.timedelta(days=7)
    # last_week_str = last_week.isoformat() + "T00:00:00Z"
    # subscription_videos_filtered = fetcher.get_subscriptions_feed(max_results=5, published_after=last_week_str)
    # if subscription_videos_filtered:
    #     for video in subscription_videos_filtered:
    #         try:
    #             title = video['snippet']['title']
    #             channel_title = video['snippet']['channelTitle']
    #             video_id = video['id']['videoId'] if 'videoId' in video['id'] else video['id']
    #             published_at = video['snippet']['publishedAt']
    #             print(f"Title: {title}")
    #             print(f"Channel: {channel_title}")
    #             print(f"Video ID: {video_id}")
    #             print(f"Published At: {published_at}")
    #             print(f"URL: https://www.youtube.com/watch?v={video_id}")
    #             print("---")
    #         except KeyError as e:
    #             print(f"Missing key in video data: {e}")
    #             continue
    # else:
    #     print("No subscription videos found for the specified date range.")