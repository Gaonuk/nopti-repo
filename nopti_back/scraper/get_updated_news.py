# from scraper.hgooglenews import get_google_news
# from scraper.hhackernews import search_hackernews_sync
# from scraper.hyoutube import get_youtube_subscription_videos
# from scraper.hspotify import get_recent_and_interesting_music
import json

def get_update_news():
    interest = ["NVIDIA", "TESLA", "GOOGLE GEMINI", "META QUEST 4"]
    news_data = []
    #TODO FOR NEXT TIME
    # for topic in interest:
    #     google_news = get_google_news(topic) or []
    #     hackernews = search_hackernews_sync(topic) or []
    #     youtube_feed = get_youtube_subscription_videos() or []
    #     spotify_feed = get_recent_and_interesting_music() or []
        
    #     news_data.extend(google_news)
    #     news_data.extend(hackernews)
    #     news_data.extend(youtube_feed)
    #     news_data.extend(spotify_feed)
    
    with open('update_data_base/current_news_data.json', 'r') as json_file:
        news_data = json.load(json_file)
    
    print(news_data)

    return news_data


