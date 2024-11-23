import asyncio
import aiohttp
import json
from datetime import datetime
from bs4 import BeautifulSoup


async def fetch_story_summary(session, story_id):
    """Fetches the summary of a story asynchronously."""
    try:
        story_url = f"https://news.ycombinator.com/item?id={story_id}"
        async with session.get(story_url) as story_response:
            if story_response.status == 200:
                content = await story_response.text()
                soup = BeautifulSoup(content, "html.parser")
                comment_elements = soup.select(".comment-tree .comment")
                if comment_elements:
                    first_comment_text = comment_elements[0].get_text(
                        separator=" ", strip=True
                    )
                    return (
                        first_comment_text[:200] + "..."
                        if len(first_comment_text) > 200
                        else first_comment_text
                    )
        return "N/A"
    except Exception as e:
        print(f"Error fetching summary for story {story_id}: {e}")
        return "N/A"


async def search_hackernews_fast(search_query, limit=10):
    """
    Searches Hacker News for articles matching a query and returns a JSON-like list of dictionaries.
    Uses asynchronous requests for faster performance.
    """
    try:
        base_url = "https://hn.algolia.com/api/v1/search"
        params = {"query": search_query, "tags": "story", "hitsPerPage": limit}

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

            results = []
            tasks = []
            for hit in data["hits"]:
                title = hit.get("title", "N/A")
                link = hit.get("url", "N/A")
                date_timestamp = hit.get("created_at_i", None)
                date = (
                    datetime.fromtimestamp(date_timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    if date_timestamp
                    else "N/A"
                )

                summary = "N/A"  # Default summary
                if "objectID" in hit:
                    story_id = hit["objectID"]
                    tasks.append(fetch_story_summary(session, story_id))
                else:
                    tasks.append(
                        asyncio.Future()
                    )  # Add a placeholder for stories without IDs
                    tasks[-1].set_result("N/A")

                results.append(
                    {
                        "title": title,
                        "link": link,
                        "summary": summary,  # Placeholder, will be updated later
                        "date": date,
                        "passed": False,
                        "source": "Hacker News",
                    }
                )

            # Fetch summaries concurrently
            summaries = await asyncio.gather(*tasks)
            for i, summary in enumerate(summaries):
                results[i]["summary"] = summary

            return results

    except aiohttp.ClientError as e:
        print(f"Error fetching data from Hacker News API: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing data from Hacker News API: {e}")
        return None


def search_hackernews_sync(search_query, limit=10):
    """
    Synchronous wrapper function to call the asynchronous search_hackernews_fast.
    """
    try:
        return asyncio.run(search_hackernews_fast(search_query, limit))
    except Exception as e:
        print(f"Error during asynchronous search: {e}")
        return None


# if __name__ == "__main__":

#     query = "NVIDIA"
#     print(search_hackernews_sync(query))
