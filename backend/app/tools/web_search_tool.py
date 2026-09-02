from tavily import TavilyClient
from backend.app.core.config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query):
    try:
        response = client.search(
            query=query,
            max_results=3,
            include_answer=True,
        )

        if response.get("answer"):
            return response["answer"]

        results = response.get("results", [])

        if not results:
            return "No information found."

        return "\n\n".join(
            item.get("content") or item.get("title", "")
            for item in results
        )

    except Exception:
        
        return "Web search failed."