from collections.abc import AsyncGenerator
from enum import Enum

import tiktoken
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessage

from app.agents.adaptor.llm_interface import ILLMAdapter
from app.agents.context.schema import (
    TOOL_CHOICE_TYPE,
    Message,
    Role,
    ToolChoice,
)
from app.agents.context.token_manager import TokenCounter
from app.common.exceptions.custom_exceptions import TokenLimitError
from app.common.llm_clients.openai_client import OpenAILLMClient
from app.common.logger import logger

MULTIMODAL_MODELS = [
    "o1",
    "o3-mini",
    "o4-mini",
    "gpt-4-vision-preview",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4.1",
    "openai/o1",
    "openai/o3-mini",
    "openai/o4-mini",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4",
]


class OpenAILLMAdapter(OpenAILLMClient, ILLMAdapter):
    """LLM API 클라이언트와 토큰 계산 기능을 결합한 에이전트용 어댑터입니다."""

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

        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # TODO: TokenCounter의 역할을 어뎁터에서 중복으로 구현하고 있음. 추후 리팩토링 필요
        self.token_counter = TokenCounter(self.tokenizer)
        self.total_input_tokens = 0
        self.total_completion_tokens = 0
        self.max_input_tokens = kwargs.get("max_input_tokens", None)
        self._supports_images = self.model in MULTIMODAL_MODELS

    def update_token_count(self, prompt_tokens: int, completion_tokens: int = 0):
        """에이전트의 누적 토큰 사용량을 업데이트하고 로그를 기록합니다."""
        self.total_input_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        logger.info(
            f"Max Input Tokens={self.max_input_tokens}, Max Completion Tokens={self._params.get('max_tokens', 1024)}, "
            f"Token usage: Input={prompt_tokens}, Completion={completion_tokens}, "
            f"Cumulative Input={self.total_input_tokens}, Cumulative Completion={self.total_completion_tokens}"
        )

    def _check_token_limit(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> int:
        """API 요청 전 누적 토큰 사용량을 계산하고, 제한을 초과하는 경우 예외를 발생시킵니다."""
        input_tokens = self.token_counter.count_message_tokens(messages)
        if tools:
            input_tokens += self.token_counter.count_text(str(tools))

        if (
            self.max_input_tokens
            and (self.total_input_tokens + input_tokens) > self.max_input_tokens
        ):
            error_message = (
                f"Request may exceed input token limit (Current: {self.total_input_tokens}, "
                f"Needed: {input_tokens}, Max: {self.max_input_tokens})"
            )
            raise TokenLimitError(error_message)
        return input_tokens

    @staticmethod
    def _format_messages(
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None,
        supports_images: bool,
    ) -> tuple[str, list[dict]]:
        """에이전트의 메시지 형식을 LLM API가 요구하는 형식으로 변환합니다."""
        all_messages: list[dict | Message] = []
        if system_msgs:
            all_messages.extend(system_msgs)
        all_messages.extend(messages)

        formatted_messages = []
        for msg in all_messages:
            if isinstance(msg, Message):
                msg_dict = msg.model_dump(exclude={"metadata"}, exclude_none=True)
            else:
                msg_dict = msg.copy()
                msg_dict.pop("metadata", None)

            if isinstance(msg_dict.get("role"), Enum):
                msg_dict["role"] = msg_dict["role"].value

            if not supports_images and isinstance(msg_dict.get("content"), list):
                msg_dict["content"] = " ".join(
                    item.get("text", "")
                    for item in msg_dict["content"]
                    if item.get("type") == "text"
                )
            formatted_messages.append(msg_dict)

        system_prompt = ""
        chat_messages = []
        if formatted_messages and formatted_messages[0]["role"] == Role.SYSTEM.value:
            system_prompt = formatted_messages[0].get("content", "")
            chat_messages = formatted_messages[1:]
        else:
            chat_messages = formatted_messages

        return system_prompt, chat_messages

    async def ask(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        **kwargs,
    ) -> ChatCompletionMessage | None:
        """LLM에 도구 사용을 요청하고 응답을 반환합니다."""
        system_prompt, chat_messages = self._format_messages(
            messages, system_msgs, self._supports_images
        )
        self._check_token_limit(chat_messages)

        response = await super().agenerate(
            system_prompt=system_prompt,
            chat_messages=chat_messages,
            **kwargs,
        )
        if response and response.usage:
            self.update_token_count(
                response.usage.prompt_tokens, response.usage.completion_tokens
            )

        return response.choices[0].message.content

    async def ask_streaming(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """LLM에 메시지 사용을 요청하고 응답을 스트리밍으로 반환합니다."""
        system_prompt, chat_messages = self._format_messages(
            messages, system_msgs, self._supports_images
        )
        self._check_token_limit(chat_messages)
        stream = super().agenerate_stream(
            system_prompt=system_prompt,
            chat_messages=chat_messages,
            **kwargs,
        )

        completion_text = ""
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                completion_text += chunk.choices[0].delta.content
            yield chunk

        completion_tokens = self.token_counter.count_text(completion_text)
        self.update_token_count(0, completion_tokens)

    async def ask_tool(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        tools: list[dict] | None = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,
        **kwargs,
    ) -> ChatCompletionMessage | None:
        """LLM에 도구 사용을 요청하고 응답을 반환합니다."""
        system_prompt, chat_messages = self._format_messages(
            messages, system_msgs, self._supports_images
        )
        self._check_token_limit(chat_messages, tools)

        response = await super().agenerate(
            system_prompt=system_prompt,
            chat_messages=chat_messages,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )

        if response and response.usage:
            self.update_token_count(
                response.usage.prompt_tokens, response.usage.completion_tokens
            )

        return response.choices[0].message if response and response.choices else None

    async def ask_tool_streaming(
        self,
        messages: list[dict | Message],
        system_msgs: list[dict | Message] | None = None,
        tools: list[dict] | None = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """LLM에 도구 사용을 요청하고 응답을 스트리밍으로 반환합니다."""
        system_prompt, chat_messages = self._format_messages(
            messages, system_msgs, self._supports_images
        )
        prompt_tokens = self._check_token_limit(chat_messages, tools)
        self.update_token_count(prompt_tokens)

        # 부모 클래스의 agenerate_stream을 호출하여 스트리밍 재시도 로직을 활용합니다.
        stream = super().agenerate_stream(
            system_prompt=system_prompt,
            chat_messages=chat_messages,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )

        completion_text = ""
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                completion_text += chunk.choices[0].delta.content
            yield chunk

        completion_tokens = self.token_counter.count_text(completion_text)
        self.update_token_count(0, completion_tokens)
