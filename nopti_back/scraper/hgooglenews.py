from GoogleNews import GoogleNews


def get_latest_relevant_news_json(search_query):
    """
    Retrieves the 10 latest and most relevant news results
    related to a given search query in JSON format.

    Args:
        search_query: The search query string.

    Returns:
        A JSON string representing a list of dictionaries,
        where each dictionary represents a news article and contains
        "title", "link", "date", and "summary" information.
        Returns an empty JSON list if no results are found.
    """
    googlenews = GoogleNews()
    googlenews.search(search_query)  # Search for the query
    results = googlenews.result()  # Get initial results

    # Further refine results (e.g., by relevance or recency if possible with the API)
    #  Here, sorting by date as a proxy for relevance/recency is done
    #  More advanced relevance ranking would require access to article content or
    #  using a separate NLP-based approach.
    results.sort(key=lambda x: x.get("date"), reverse=True)

    formatted_results = []
    for item in results[:10]:
        formatted_results.append(
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "date": item.get("date"),
                "summary": item.get("desc"),
                "passed": False,
                "source": "Google News",
            }
        )

    return formatted_results


def get_google_news(search_query):
    """
    Wrapper function that calls get_latest_relevant_news_json
    with the provided search query.
    """
    return get_latest_relevant_news_json(search_query)


# if __name__ == "__main__":
#     search_query = "NVIDIA"
#     latest_news_json = get_google_news(search_query)
#     print(latest_news_json)
