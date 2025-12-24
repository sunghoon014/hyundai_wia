"""Search tools using Perplexity Sonar Pro via OpenRouter for web search capabilities."""

import json
from dataclasses import asdict

from fastmcp import FastMCP

from app.agents.tools.web_search.containers import SearchContainer

search_mcp_server = FastMCP("LLM with Search MCP Server")
search_container = SearchContainer()
llm_adaptor_for_search = search_container.llm_adaptor_for_search()


@search_mcp_server.tool(
    name="web_search",
    description="최신 정보, 실시간 사건, 또는 외부 세계의 공개된 사실을 찾기 위해 웹을 검색합니다. 검색 정확도를 높이기 위해 대화 기록을 분석하여 구체적이고 상세한 검색어(query)를 전달해야 합니다.",
)
async def web_search(query: str, params: dict | None = None) -> str:
    """Performs a direct web search using the provided query.

    Args:
        query: The search query to execute.
        params: Optional dictionary of additional parameters for the search.

    Returns:
        A JSON string of the search results, including content and citations.
    """
    try:
        result = await llm_adaptor_for_search.asearch(query, **(params or {}))
        # Use asdict for dataclass conversion, ensure result is a dataclass instance
        return json.dumps(asdict(result), ensure_ascii=False)
    except Exception as e:
        return f"Error performing web search: {str(e)}"


if __name__ == "__main__":
    search_mcp_server.run()
