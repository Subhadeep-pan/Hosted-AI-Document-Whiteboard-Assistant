"""News search tool - same Tavily account as web_search_tool.py, but
scoped to the "news" topic so results are recent articles rather than
general web pages."""

from tavily import TavilyClient
from backend.app.core.config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)


def search_news(query):
    try:
        response = client.search(
            query=query,
            topic="news",
            max_results=3,
            include_answer=True,
        )

        if response.get("answer"):
            return response["answer"]

        results = response.get("results", [])

        if not results:
            return "No recent news found."

        return "\n\n".join(
            item.get("content") or item.get("title", "")
            for item in results
        )

    except Exception:
        return "News search failed."
