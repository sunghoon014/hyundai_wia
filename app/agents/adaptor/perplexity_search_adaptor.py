import asyncio
from dataclasses import dataclass
from typing import TypedDict, TypeVar

from app.common.llm_clients.openai_client import OpenAILLMClient

T = TypeVar("T")


class ToolCallResult(TypedDict):
    tool_name: str
    tool_args: dict


@dataclass
class PerplexitySearchURLCitation:
    title: str
    url: str


@dataclass
class PerplexitySearchResponse:
    content: str
    citations: list[PerplexitySearchURLCitation]


class PerplexitySearchLLMAdaptor(OpenAILLMClient):
    """Perplexity Search LLM Client.

    Doc: https://platform.openai.com/docs/guides/tools-web-search / https://openrouter.ai/docs/features/web-search#perplexity-model-pricing
    """

    def __init__(
        self,
        model: str,
        provider: str,
        api_key: str = None,
        params: dict = None,
        **kwargs,
    ):
        super().__init__(
            model=model,
            provider=provider,
            api_key=api_key,
            params=params,
            retry=kwargs.get("retry", {"max_retries": 3, "base_delay": 1.0}),
        )
        self._sync_client, self._async_client = self._create_clients()

    def _prepare_completion_params(
        self, messages: list[dict], stream: bool = False, **kwargs
    ) -> dict:
        # OpenRouter/Perplexity에서 지원하는 API 파라미터 목록
        allowed_params = {
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "seed",
        }

        # 허용된 파라미터만 필터링합니다.
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_params}

        params = {
            **self._params,
            **filtered_kwargs,
            "model": self._model,
            "messages": messages,
            "stream": stream,
        }

        return params

    async def asearch(self, query: str, **kwargs) -> PerplexitySearchResponse:
        messages = [{"role": "user", "content": query}]
        params = self._prepare_completion_params(messages, False, **kwargs)
        response = await self._async_client.chat.completions.create(**params)

        message = response.choices[0].message
        content = message.content.strip() if message.content else ""

        citations = []
        # OpenRouter를 통해 Perplexity API를 사용하면 'annotations' 필드에 인용(citation) 정보가 포함됩니다.
        if hasattr(message, "annotations") and message.annotations:
            for annotation in message.annotations:
                if hasattr(annotation, "url_citation") and annotation.url_citation:
                    citations.append(
                        PerplexitySearchURLCitation(
                            title=annotation.url_citation.title,
                            url=annotation.url_citation.url,
                        )
                    )

        return PerplexitySearchResponse(content=content, citations=citations)

    def search(self, query: str, **kwargs) -> PerplexitySearchResponse:
        return asyncio.run(self.asearch(query, **kwargs))
