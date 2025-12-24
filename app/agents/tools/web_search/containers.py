from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from app.agents.adaptor.perplexity_search_adaptor import PerplexitySearchLLMAdaptor
from app.config.utils import init_config


class SearchContainer(DeclarativeContainer):
    """Dependency injection container for search tools."""

    config = Configuration()
    init_config(config)
    web_search_config = config.mcp_tools.web_search()
    llm_adaptor_for_search = Singleton(
        PerplexitySearchLLMAdaptor,
        model=web_search_config.get("model"),
        provider=web_search_config.get("provider"),
        api_key=config.openrouter.api_key()
        if web_search_config.get("provider") == "openrouter"
        else config.openai.api_key(),
        params=web_search_config.get("params"),
    )
