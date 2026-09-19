import os
from tavily import TavilyClient

from app.config import TAVILY_API_KEY


def search_web(query: str, max_results: int = 5):
    """
    Search the web using Tavily.
    """

    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not configured.")

    client = TavilyClient(api_key=TAVILY_API_KEY)

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
    )

    return response["results"]