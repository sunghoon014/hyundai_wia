from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from app.config.utils import init_config


class RetrievalContainer(DeclarativeContainer):
    """Dependency injection container for search tools."""

    config = Configuration()
    init_config(config)
