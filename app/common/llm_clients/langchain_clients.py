import base64
import os
from collections.abc import Generator
from typing import Any

import langchain
import requests
from langchain_community.cache import InMemoryCache
from langchain_openai import ChatOpenAI

from app.common.llm_clients.langchain_interface import ILangchainClient
from app.common.logger import logger

langchain.llm_cache = InMemoryCache()


class LangchainClient(ILangchainClient):
    def __init__(self, model: str, provider: str, api_key: str, params: dict):
        self._model = model
        self._provider = provider
        self._api_key = api_key
        self._params = params
        self._client = self._create_clients()

    def _create_clients(self):
        if self._provider == "openrouter":
            logger.info(f"Creating OpenRouter client: {self._model}")
            return ChatOpenAI(
                model=self._model,
                openai_api_key=self._api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                **self._params,
            )
        else:
            logger.info(f"Creating OpenAI client: {self._model}")
            return ChatOpenAI(
                model=self._model,
                openai_api_key=self._api_key,
                **self._params,
            )

    def create_messages(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> list[dict[str, Any]]:
        """Langchain 모델에 전달할 메시지 목록을 생성합니다.

        Args:
            system_prompt: 사용할 시스템 프롬프트
            user_prompt: 사용할 사용자 프롬프트
        Returns:
            Langchain 모델 형식에 맞는 메시지 목록.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return messages

    def invoke(
        self,
        system_prompt: str,
        user_prompt: str,
        chat_history: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Invoke the model.

        Args:
            system_prompt: The system prompt.
            user_prompt: The user prompt.
            chat_history: The chat history.
        """
        messages = self.create_messages(system_prompt, user_prompt)
        if chat_history:
            messages = chat_history + messages

        return self._client.invoke(messages)

    def invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        format_type: dict[str, Any],
        chat_history: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Invoke the model with structured output."""
        structured_llm = self._client.with_structured_output(format_type)
        messages = self.create_messages(system_prompt, user_prompt)
        if chat_history:
            messages = chat_history + messages
        return structured_llm.invoke(messages)

    def batch(
        self,
        system_prompts: list[str],
        user_prompts: list[str],
        chat_history: list[list[dict[str, Any]]] | None = None,
    ) -> list[str]:
        """Batch invoke the model.

        Args:
            system_prompts: The system prompts.
            user_prompts: The user prompts.
            chat_history: The chat history.
        """
        messages_list = []
        for i in range(len(system_prompts)):
            messages = self.create_messages(system_prompts[i], user_prompts[i])
            if chat_history:
                messages = chat_history[i] + messages
            messages_list.append(messages)

        return self._client.batch(messages_list)

    async def abatch(
        self,
        system_prompts: list[str],
        user_prompts: list[str],
        chat_history: list[list[dict[str, Any]]] | None = None,
    ) -> list[str]:
        """Async batch invoke the model."""
        messages_list = []
        for i in range(len(system_prompts)):
            messages = self.create_messages(system_prompts[i], user_prompts[i])
            if chat_history:
                messages = chat_history[i] + messages
            messages_list.append(messages)
        return await self._client.abatch(messages_list)

    async def abatch_structured(
        self,
        system_prompts: list[str],
        user_prompts: list[str],
        format_type: dict[str, Any],
        chat_history: list[list[dict[str, Any]]] | None = None,
    ) -> list[str]:
        """Async batch invoke the model."""
        structured_llm = self._client.with_structured_output(format_type)
        messages_list = []
        for i in range(len(system_prompts)):
            messages = self.create_messages(system_prompts[i], user_prompts[i])
            if chat_history:
                messages = chat_history[i] + messages
            messages_list.append(messages)
        return await structured_llm.abatch(messages_list)

    def stream(
        self,
        system_prompt: str,
        user_prompt: str,
        chat_history: list[dict[str, Any]] | None = None,
    ) -> Generator[Any, None, None]:
        """Stream the model.

        Args:
            system_prompt: The system prompt.
            user_prompt: The user prompt.
            chat_history: The chat history.
        """
        messages = self.create_messages(system_prompt, user_prompt)
        if chat_history:
            messages = chat_history + messages

        yield from self._client.stream(messages)


class MultiModalLangchainClient(LangchainClient):
    def __init__(self, model: str, provider: str, api_key: str, params: dict):
        super().__init__(model, provider, api_key, params)

    def encode_image_from_url(self, url):
        """이미지를 base64로 인코딩하는 함수 (URL)."""
        response = requests.get(url)
        if response.status_code == 200:
            image_content = response.content
            if url.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif url.lower().endswith(".png"):
                mime_type = "image/png"
            else:
                mime_type = "image/unknown"
            return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"
        else:
            raise Exception("Failed to download image")

    def encode_image_from_file(self, file_path):
        """이미지를 base64로 인코딩하는 함수 (파일 경로)."""
        with open(file_path, "rb") as image_file:
            image_content = image_file.read()
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif file_ext == ".png":
                mime_type = "image/png"
            else:
                mime_type = "image/unknown"
            return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"

    def encode_image_from_bytes(
        self, image_bytes: bytes, mime_type: str = "image/png"
    ) -> str:
        """주어진 이미지 바이트를 Base64 데이터 URL로 인코딩하는 함수."""
        if not isinstance(image_bytes, bytes):
            raise TypeError("image_bytes must be of type bytes")
        return (
            f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        )

    def create_messages_with_image(
        self,
        image_input: str | bytes,
        system_prompt: str,
        user_prompt: str,
        mime_type: str = "image/png",
    ) -> list[dict[str, Any]]:
        """Langchain 모델에 전달할 메시지 목록을 생성합니다. 이미지 URL, 파일 경로 또는 바이트 데이터를 입력받습니다.

        Args:
            image_input: 이미지 URL(str), 로컬 파일 경로(str), 또는 이미지 바이트(bytes).
            system_prompt: 사용할 시스템 프롬프트.
            user_prompt: 사용할 사용자 프롬프트.
            mime_type: image_input이 바이트일 경우 사용할 MIME 타입.

        Returns:
            Langchain 모델 형식에 맞는 메시지 목록.
        """
        encoded_image = None
        if isinstance(image_input, str):
            if image_input.startswith("http://") or image_input.startswith("https://"):
                encoded_image = self.encode_image_from_url(image_input)
            else:
                encoded_image = self.encode_image_from_file(image_input)
        elif isinstance(image_input, bytes):
            encoded_image = self.encode_image_from_bytes(image_input, mime_type)
        else:
            raise TypeError(
                "image_input must be a URL (str), file path (str), or bytes"
            )

        user_content = [
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {"url": encoded_image}},
        ]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        return messages

    def invoke(
        self,
        image_input: str | bytes,
        system_prompt: str,
        user_prompt: str,
        mime_type: str = "image/png",
        chat_history: list[dict[str, Any]] | None = None,
    ):
        """Invoke the model."""
        messages = self.create_messages_with_image(
            image_input, system_prompt, user_prompt, mime_type
        )
        if chat_history:
            messages = chat_history + messages

        return self._client.invoke(messages)

    def batch(
        self,
        image_inputs: list[str | bytes],
        system_prompts: list[str],
        user_prompts: list[str],
        mime_types: list[str],
        chat_history: list[list[dict[str, Any]]] | None = None,
    ) -> list[str]:
        """Batch invoke the model."""
        if not (
            len(system_prompts)
            == len(user_prompts)
            == len(mime_types)
            == len(image_inputs)
        ):
            raise ValueError(
                "Length of all input lists must match the number of images."
            )

        messages_list = []
        for i in range(len(system_prompts)):
            messages = self.create_messages_with_image(
                image_inputs[i], system_prompts[i], user_prompts[i], mime_types[i]
            )
            if chat_history:
                messages = chat_history[i] + messages
            messages_list.append(messages)

        return self._client.batch(messages_list)

    def stream(
        self,
        image_input: str | bytes,
        system_prompt: str,
        user_prompt: str,
        mime_type: str = "image/png",
        chat_history: list[dict[str, Any]] | None = None,
    ) -> Generator[Any, None, None]:
        """Stream the model."""
        messages = self.create_messages_with_image(
            image_input, system_prompt, user_prompt, mime_type
        )
        if chat_history:
            messages = chat_history + messages

        yield from self._client.stream(messages)
