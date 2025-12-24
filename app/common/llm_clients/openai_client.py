import asyncio
import base64
import mimetypes
import time
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

from openai import APIError, AsyncOpenAI, AuthenticationError, OpenAI, RateLimitError
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from tenacity import (
    AsyncRetrying,
    Retrying,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.common.llm_clients.interface import ILLMClient
from app.common.logger import logger

REASONING_MODELS = ["o1", "o3-mini", "openai/o3-mini", "openai/o4-mini"]


def _log_before_sleep(retry_state):
    """재시도 전 로그를 기록하는 tenacity 콜백 함수입니다."""
    exception = retry_state.outcome.exception()
    logger.warning(
        f"API error occurred: {exception}. "
        f"Retrying in {retry_state.next_action.sleep:.2f} seconds..."
    )


class OpenAILLMClient(ILLMClient):
    def __init__(
        self,
        model: str,
        provider: str,
        api_key: str = None,
        params: dict = None,
        **kwargs,
    ):
        self._model = model
        self._provider = provider
        self._api_key = api_key
        self._params = params
        self._config = kwargs
        self._sync_client, self._async_client = self._create_clients()

    def _create_clients(self) -> tuple[OpenAI, AsyncOpenAI]:
        """OpenAI 라이브러리와 호환되는 클라이언트를 생성합니다."""
        if self._provider == "openrouter":
            client_config = {
                "api_key": self._api_key,
                "base_url": "https://openrouter.ai/api/v1",
            }
            logger.info("Creating OpenRouter client.")
            return OpenAI(**client_config), AsyncOpenAI(**client_config)
        else:
            client_config = {"api_key": self._api_key}
            logger.info("Creating default OpenAI client.")
            return OpenAI(**client_config), AsyncOpenAI(**client_config)

    def _image_to_data_url(self, image_input: str | bytes) -> str:
        """이미지 파일 경로, URL 또는 바이트를 data URL로 변환합니다."""
        if isinstance(image_input, bytes):
            # 바이트 데이터 처리
            mime_type = "image/png"  # 기본값, 필요시 추론 로직 추가 가능
            base64_data = base64.b64encode(image_input).decode("utf-8")
            return f"data:{mime_type};base64,{base64_data}"

        if not isinstance(image_input, str):
            raise TypeError("Unsupported image input type")

        # URL 또는 데이터 URL은 그대로 반환
        if image_input.startswith(("http://", "https://", "data:")):
            return image_input

        # 로컬 파일 경로 처리
        try:
            file_path_str = (
                image_input[7:] if image_input.startswith("file://") else image_input
            )
            path_obj = Path(file_path_str)

            if not path_obj.exists() or not path_obj.is_file():
                logger.warning(f"Local file not found: {file_path_str}")
                return image_input  # 변환 실패 시 원본 반환

            mime_type, _ = mimetypes.guess_type(str(path_obj))
            if not mime_type or not mime_type.startswith("image/"):
                mime_type = "image/jpeg"  # 기본 MIME 타입

            with open(path_obj, "rb") as f:
                file_data = f.read()

            base64_data = base64.b64encode(file_data).decode("utf-8")
            return f"data:{mime_type};base64,{base64_data}"

        except Exception as e:
            logger.error(f"Failed to convert file {image_input} to data URL: {e}")
            return image_input

    def _validate_and_prepare_messages(
        self,
        system_prompt: str,
        chat_messages: list[dict] | None = None,
        images: list[str | dict | bytes] | None = None,
    ) -> list[dict]:
        """메시지 검증 및 준비."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if chat_messages:
            messages.extend(chat_messages)

        # 이미지 처리
        if images:
            # 이미지를 추가할 사용자 메시지를 찾거나 생성합니다.
            if not messages or messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": []})

            last_msg = messages[-1]
            content = last_msg.get("content", "")

            # content를 리스트 형태로 변환합니다.
            if isinstance(content, str):
                content = [{"type": "text", "text": content}] if content else []
            elif not isinstance(content, list):
                content = []

            # 이미지 추가
            for img in images:
                if isinstance(img, dict):  # 기존 dict 형식 지원
                    content.append(img)
                else:  # str (경로/URL) 또는 bytes
                    data_url = self._image_to_data_url(img)
                    content.append(
                        {"type": "image_url", "image_url": {"url": data_url}}
                    )

            last_msg["content"] = content

        return messages

    def _prepare_completion_params(
        self, messages: list[dict], stream: bool = False, **kwargs
    ) -> dict:
        """허용된 파라미터 외에는 필터링합니다."""
        allowed_params = {
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "seed",
            "n",
            "response_format",
            "tools",
            "tool_choice",
            "logit_bias",
            "logprobs",
            "top_logprobs",
            "user",
            # 일부 모델용 특수 파라미터
            "reasoning_effort",
            "max_completion_tokens",
        }

        # 1. 기본 파라미터로 시작합니다.
        params = self._params.copy()

        # 2. kwargs에서 허용된 파라미터만 필터링하여 덮어씁니다.
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_params}
        params.update(filtered_kwargs)

        # 3. 모델별 특수 파라미터를 처리합니다.
        if self._model in REASONING_MODELS:
            params["max_completion_tokens"] = params.pop("max_tokens", 1024)
            params.setdefault("reasoning_effort", "medium")
            params.pop("temperature", None)
        else:
            # 일반 모델의 기본값을 설정합니다.
            params.setdefault("max_tokens", 1024)
            params.setdefault("temperature", 0.0)

        # 4. 필수 파라미터를 추가합니다.
        params["model"] = self._model
        params["messages"] = messages
        params["stream"] = stream

        return params

    @property
    def model(self) -> str:
        return self._model

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        before_sleep=_log_before_sleep,
    )
    async def agenerate(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        images: list[str | dict] | None = None,
        **kwargs,
    ) -> ChatCompletion:
        messages = self._validate_and_prepare_messages(
            system_prompt, chat_messages, images
        )

        params = self._prepare_completion_params(messages, stream=False, **kwargs)

        # API 호출
        response = await self._async_client.chat.completions.create(**params)
        return response

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        before_sleep=_log_before_sleep,
    )
    async def agenerate_structured(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        images: list[str | dict] | None = None,
        response_format: dict | None = None,
        **kwargs,
    ) -> ChatCompletion:
        if response_format is None:
            raise ValueError("response_format is required for structured generation")

        messages = self._validate_and_prepare_messages(
            system_prompt, chat_messages, images
        )
        params = self._prepare_completion_params(messages, stream=False, **kwargs)
        if "stream" in params:
            params.pop("stream")

        params["response_format"] = response_format

        response = await self._async_client.chat.completions.parse(**params)
        return response

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        before_sleep=_log_before_sleep,
    )
    async def abatch_generate_structured(
        self,
        system_prompts: list[str],
        list_chat_messages: list[list[dict[str, any]]],
        response_format: dict | None = None,
        **kwargs,
    ) -> list[ChatCompletion]:
        if response_format is None:
            raise ValueError("response_format is required for structured generation")

        tasks = []
        for system_prompt, chat_messages in zip(
            system_prompts, list_chat_messages, strict=False
        ):
            messages = self._validate_and_prepare_messages(system_prompt, chat_messages)
            params = self._prepare_completion_params(messages, stream=False, **kwargs)
            if "stream" in params:
                params.pop("stream")
            params["response_format"] = response_format
            tasks.append(self._async_client.chat.completions.parse(**params))

        results = await asyncio.gather(*tasks)
        return results

    async def agenerate_stream(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        images: list[str | dict] | None = None,
        **kwargs,
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        retry_config = self._config.get("retry", {})
        retryer = AsyncRetrying(
            stop=stop_after_attempt(retry_config.get("max_retries", 3)),
            wait=wait_random_exponential(min=1, max=60),
            retry=retry_if_exception_type((RateLimitError, APIError)),
            before_sleep=_log_before_sleep,
        )

        try:
            async for attempt in retryer:
                with attempt:
                    messages = self._validate_and_prepare_messages(
                        system_prompt, chat_messages, images
                    )
                    params = self._prepare_completion_params(
                        messages, stream=True, **kwargs
                    )
                    stream = await self._async_client.chat.completions.create(**params)
                    async for chunk in stream:
                        yield chunk
                    return
        except AuthenticationError as e:
            logger.warning(
                f"Authentication error: {e}. Re-creating client and retrying once..."
            )
            self._sync_client, self._async_client = self._create_clients()
            await asyncio.sleep(1)
            # 클라이언트 재생성 후 마지막으로 한 번 더 시도합니다.
            messages = self._validate_and_prepare_messages(
                system_prompt, chat_messages, images
            )
            params = self._prepare_completion_params(messages, stream=True, **kwargs)
            stream = await self._async_client.chat.completions.create(**params)
            async for chunk in stream:
                yield chunk

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        before_sleep=_log_before_sleep,
    )
    def generate(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        images: list[str | dict] | None = None,
        **kwargs,
    ) -> ChatCompletion:
        messages = self._validate_and_prepare_messages(
            system_prompt, chat_messages, images
        )

        params = self._prepare_completion_params(messages, stream=False, **kwargs)
        response = self._sync_client.chat.completions.create(**params)
        return response

    def generate_stream(
        self,
        system_prompt: str,
        chat_messages: list[dict[str, any]] | None = None,
        images: list[str | dict] | None = None,
        **kwargs,
    ) -> Generator[ChatCompletionChunk, None, None]:
        retry_config = self._config.get("retry", {})
        retryer = Retrying(
            stop=stop_after_attempt(retry_config.get("max_retries", 3)),
            wait=wait_random_exponential(min=1, max=60),
            retry=retry_if_exception_type((RateLimitError, APIError)),
            before_sleep=_log_before_sleep,
        )

        try:
            for attempt in retryer:
                with attempt:
                    messages = self._validate_and_prepare_messages(
                        system_prompt, chat_messages, images
                    )
                    params = self._prepare_completion_params(
                        messages, stream=True, **kwargs
                    )
                    stream = self._sync_client.chat.completions.create(**params)
                    yield from stream
                    return
        except AuthenticationError as e:
            logger.warning(
                f"Authentication error: {e}. Re-creating client and retrying once..."
            )
            self._sync_client, self._async_client = self._create_clients()
            time.sleep(1)
            messages = self._validate_and_prepare_messages(
                system_prompt, chat_messages, images
            )
            params = self._prepare_completion_params(messages, stream=True, **kwargs)
            stream = self._sync_client.chat.completions.create(**params)
            yield from stream
