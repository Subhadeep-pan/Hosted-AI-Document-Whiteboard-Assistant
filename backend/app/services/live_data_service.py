"""
Live-data orchestration (Sections 8, 9, 13 of the upgrade plan).

Chooses which live tool(s) to call for a question that needs fresh
external information. Design principle from the plan (section 13):
don't add tools just to look bigger - pick the source that actually
fits the question.
"""

from backend.app.tools.web_search_tool import search_web
from backend.app.tools.news_tool import search_news
from backend.app.tools.api_tool import call_api_tool

NEWS_KEYWORDS = ["news", "headline", "breaking"]
API_KEYWORDS = ["weather", "temperature", "forecast"]


def fetch_live_data(question):
    """Returns {"text": ..., "tool_used": ...} - the planner already
    decided live data is needed; this just decides which live tool."""

    lowered = question.lower()

    if any(word in lowered for word in API_KEYWORDS):
        return {"text": call_api_tool(question), "tool_used": "api_tool"}

    if any(word in lowered for word in NEWS_KEYWORDS):
        return {"text": search_news(question), "tool_used": "news_tool"}

    return {"text": search_web(question), "tool_used": "web_search_tool"}
