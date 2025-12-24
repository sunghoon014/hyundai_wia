import asyncio
from typing import Any

from app.common.llm_clients.langchain_interface import ILangchainClient
from app.common.logger import logger


class LangchainAdapter:
    def __init__(
        self,
        llm_client: ILangchainClient | None = None,
        multi_modal_client: ILangchainClient | None = None,
    ):
        self.llm_client = llm_client
        self.multi_modal_client = multi_modal_client

    async def _run_sync_in_executor(self, func, *args, **kwargs):
        """Helper to run sync functions in executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def llm_client_ainvoke(self, system_prompt: str, user_prompt: str) -> Any:
        try:
            response = await self._run_sync_in_executor(
                self.llm_client.invoke,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            return response
        except Exception as e:
            logger.error(f"Error invoking model: {e}")
            raise e

    async def llm_client_abatch(
        self,
        system_prompts: str,
        user_prompts: str,
        chat_history: list[list[dict[str, Any]]] | None = None,
    ) -> Any:
        try:
            response = await self._run_sync_in_executor(
                self.llm_client.batch,
                system_prompts=system_prompts,
                user_prompts=user_prompts,
                chat_history=chat_history,
            )
            return response
        except Exception as e:
            logger.error(f"Error batching model: {e}")
            raise e

    async def multi_modal_client_abatch(
        self,
        image_inputs: list[str | bytes],
        system_prompts: list[str] | None = None,
        user_prompts: list[str] | None = None,
        mime_types: list[str] | None = None,
        chat_history: list[list[dict[str, Any]]] | None = None,
    ) -> Any:
        try:
            response = await self._run_sync_in_executor(
                self.multi_modal_client.batch,
                image_inputs=image_inputs,
                system_prompts=system_prompts,
                user_prompts=user_prompts,
                mime_types=mime_types,
                chat_history=chat_history,
            )
            return response
        except Exception as e:
            logger.error(f"Error batching model: {e}")
            raise e
