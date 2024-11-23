import asyncio
from crawl4ai import AsyncWebCrawler

nom_utulisateur_mac = "davidperso"

async def scrape_youtube_with_profile_mac():
    """Scrapes video titles and links from YouTube using an existing Chrome profile."""
    chrome_user_data_dir = f"/Users/{nom_utulisateur_mac}/Library/Application Support/Google/Chrome/Default"  # Update with your path

    async with AsyncWebCrawler(
        browser_type="chromium",          # Use Chromium browser
        use_managed_browser=True,  # Use the system's default browser
        headless=False,                  # Show browser GUI for debugging
        user_data_dir=chrome_user_data_dir,  # Use your Chrome profile  
    ) as crawler:
        result = await crawler.arun(
            url="https://www.youtube.com",
            wait_for="css:#content",     # Wait for the main content to load
            js_code=[
                    "let totalHeight = 0;",
                    "const distance = 100;",
                    "const scrollInterval = setInterval(() => {",
                    "  window.scrollBy(0, distance);",
                    "  totalHeight += distance;",
                    "  if (totalHeight >= document.body.scrollHeight) {",
                    "    clearInterval(scrollInterval);",
                    "  }",
                    "}, 200); // <-- Added missing closing parenthesis and semicolon here"
                ],
            delay_before_return_html=3.0,   # Wait for content to render
            css_selector="ytd-rich-item-renderer"  # Select video containers
        )

        if result.success:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html, 'html.parser')
            videos = []
            for video in soup.select("ytd-rich-item-renderer"):
                title = video.select_one("#video-title").text.strip() if video.select_one("#video-title") else "No Title"
                link = "https://www.youtube.com" + video.select_one("#video-title")['href'] if video.select_one("#video-title") else "No Link"
                videos.append({"title": title, "link": link})

            print(f"Extracted {len(videos)} videos:")
            for video in videos:
                print(f"{video['title']} -> {video['link']}")
        else:
            print(f"Failed to scrape YouTube: {result.error_message}")

asyncio.run(scrape_youtube_with_profile_mac())

# import asyncio
# from crawl4ai import AsyncWebCrawler

# async def scrape_youtube_feed():
#     """Scrapes your YouTube feed using your Chrome browser profile."""

#     async with AsyncWebCrawler(
#         headless=False,  # Open the browser visibly
#         use_managed_browser=True,  # Use the system's default browser
#         browser_type="chromium", # Specify Chromium (Chrome)
#         user_data_dir = "/path/to/your/chrome/profile", # Important!
#     ) as crawler:
#         result = await crawler.arun(url="https://www.youtube.com/")
#         print(result.html)

# # Replace with the actual path to your Chrome profile directory
# # On macOS: /Users/<YourUserName>/Library/Application Support/Google/Chrome/Default
# # On Windows: C:\\Users\\<YourUserName>\\AppData\\Local\\Google\\Chrome\\User Data\\Default
# # On Linux: /home/<YourUserName>/.config/google-chrome/Default/
# user_data_dir =  f"/Users/{nom_utulisateur_mac}/Library/Application Support/Google/Chrome/Default"

# asyncio.run(scrape_youtube_feed())