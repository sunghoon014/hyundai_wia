from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any


class ILangchainClient(ABC):
    @abstractmethod
    def invoke(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def batch(self, **kwargs: Any) -> list[str]:
        pass

    @abstractmethod
    def stream(self, **kwargs: Any) -> Generator[Any, None, None]:
        pass
