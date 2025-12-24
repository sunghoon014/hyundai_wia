import base64
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.runnables import Runnable

from app.common.logger import logger
from app.domains.document.handlers.node.base import BaseNode
from app.domains.document.schemas.state import ParseState


class PageSummaryNode(BaseNode):
    def __init__(
        self,
        page_summary_chain: Runnable,
        document_summary_chain: Runnable,
        page_summary_system_prompt: str,
        document_summary_system_prompt: str,
    ):
        self.name = "page_summary_node"
        self.page_summary_chain = page_summary_chain
        self.document_summary_chain = document_summary_chain
        self.page_summary_system_prompt = page_summary_system_prompt
        self.document_summary_system_prompt = document_summary_system_prompt

    def _make_batch_data(
        self, post_parse_elements: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """페이지 요약을 위한 배치 데이터 준비."""
        page_content_map = {}
        for element in post_parse_elements:
            element_page = element.get("page")
            if element_page not in page_content_map:
                page_content_map[element_page] = []
            element_text = element.get("content").get("markdown")
            page_content_map[element_page].append(element_text)

        data_batches = []
        for page, content in page_content_map.items():
            data_batches.append(
                {
                    "system_prompt": self.page_summary_system_prompt,
                    "page": str(page),
                    "text": "\n".join(content),
                }
            )
        logger.debug(f"PageSummary system prompt: {self.page_summary_system_prompt}")
        logger.debug(f"PageSummary data_batches: {data_batches[0]}")
        logger.info(f"PageSummary data_batches_length: {len(data_batches)}")
        return data_batches

    async def execute(self, state: ParseState) -> AsyncGenerator[ParseState, None]:
        post_parse_elements = state["post_parse_elements"]
        data_batches = self._make_batch_data(post_parse_elements)
        if len(data_batches) == 0:
            logger.warning("PageSummary data batches is empty")
            yield {"page_summary": []}
        else:
            llm_results = await self.page_summary_chain.ainvoke(data_batches)
            logger.info(f"PageSummary LLM results: {len(llm_results)}")

            page_summary_result = []
            for data_batch, llm_result in zip(data_batches, llm_results, strict=False):
                page_summary_result.append(
                    {
                        "system_prompt": self.document_summary_system_prompt,
                        "page": data_batch.get("page"),
                        "page_raw": data_batch.get("text"),
                        "page_summary": llm_result.content,
                    }
                )
            logger.debug(
                f"Document summary system prompt: {self.document_summary_system_prompt}"
            )
            logger.debug(f"PageSummary result sample: {page_summary_result[0]}")
            logger.info(f"PageSummary result length: {len(page_summary_result)}")
            llm_results2 = await self.document_summary_chain.ainvoke(
                page_summary_result
            )
            logger.info(f"DocumentSummary LLM results: {llm_results2.content}")
            yield {
                "page_summary": page_summary_result,
                "document_summary": llm_results2.content,
            }


class ImageSummaryNode(BaseNode):
    def __init__(self, chain: Runnable, system_prompt: str):
        self.name = "image_summary_node"
        self.chain = chain
        self.system_prompt = system_prompt

    def _make_batch_data(
        self, post_parse_elements: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """이미지 요약을 위한 배치 데이터 준비."""
        data_batches = []
        for i in range(len(post_parse_elements)):
            if (
                post_parse_elements[i].get("category") == "figure"
                or post_parse_elements[i].get("category") == "chart"
            ):
                text = ""
                if (i > 1) and (i < len(post_parse_elements) - 2):
                    text += (
                        post_parse_elements[i - 2].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i - 1].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i + 1].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i + 2].get("content").get("markdown")
                    )
                elif (i > 0) and (i < len(post_parse_elements) - 1):
                    text += (
                        post_parse_elements[i - 1].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i + 1].get("content").get("markdown")
                    )
                else:
                    text += post_parse_elements[i].get("content").get("markdown")
                data_batches.append(
                    {
                        "system_prompt": self.system_prompt,
                        "text": text,
                        "base64_encoding": base64.b64decode(
                            post_parse_elements[i].get("base64_encoding")
                        ),
                        "mime_type": "image/jpeg",
                        "page": str(post_parse_elements[i].get("page")),
                    }
                )
        if len(data_batches) == 0:
            return []
        else:
            logger.debug(
                f"ImageSummary system prompt: {data_batches[0].get('system_prompt')}"
            )
            logger.debug(f"ImageSummary text: {data_batches[0].get('text')}")
            logger.info(f"ImageSummary data batches length: {len(data_batches)}")
            return data_batches

    async def execute(self, state: ParseState) -> AsyncGenerator[ParseState, None]:
        post_parse_elements = state["post_parse_elements"]
        data_batches = self._make_batch_data(post_parse_elements)
        if len(data_batches) == 0:
            logger.warning("ImageSummary data batches is empty")
            yield {"image_summary": []}
        else:
            llm_results = await self.chain.ainvoke(data_batches)
            logger.info(f"LLM results: {len(llm_results)}")

            result = []
            for data_batch, llm_result in zip(data_batches, llm_results, strict=False):
                result.append(
                    {
                        "page": data_batch.get("page"),
                        "image_raw": data_batch.get("text"),
                        "image_summary": llm_result.content,
                    }
                )
            logger.debug(f"ImageSummary result sample: {result[0]}")
            logger.info(f"ImageSummary result length: {len(result)}")
            yield {"image_summary": result}


class TableSummaryNode(BaseNode):
    def __init__(self, chain: Runnable, system_prompt: str):
        self.name = "table_summary_node"
        self.chain = chain
        self.system_prompt = system_prompt

    def _make_batch_data(
        self, post_parse_elements: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """테이블 요약을 위한 배치 데이터 준비."""
        data_batches = []
        for i in range(len(post_parse_elements)):
            if post_parse_elements[i].get("category") == "table":
                text = ""
                if (i > 1) and (i < len(post_parse_elements) - 2):
                    text += (
                        post_parse_elements[i - 2].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i - 1].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i + 1].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i + 2].get("content").get("markdown")
                    )
                elif (i > 0) and (i < len(post_parse_elements) - 1):
                    text += (
                        post_parse_elements[i - 1].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i].get("content").get("markdown")
                        + "\n"
                        + post_parse_elements[i + 1].get("content").get("markdown")
                    )
                else:
                    text += post_parse_elements[i].get("content").get("markdown")
                data_batches.append(
                    {
                        "system_prompt": self.system_prompt,
                        "text": text,
                        "base64_encoding": base64.b64decode(
                            post_parse_elements[i].get("base64_encoding")
                        ),
                        "mime_type": "image/jpeg",
                        "page": str(post_parse_elements[i].get("page")),
                    }
                )
        if len(data_batches) == 0:
            return []
        else:
            logger.debug(
                f"TableSummary system prompt: {data_batches[0].get('system_prompt')}"
            )
            logger.debug(f"TableSummary text: {data_batches[0].get('text')}")
            logger.info(f"TableSummary data batches length: {len(data_batches)}")
            return data_batches

    async def execute(self, state: ParseState) -> AsyncGenerator[ParseState, None]:
        post_parse_elements = state["post_parse_elements"]
        data_batches = self._make_batch_data(post_parse_elements)
        if len(data_batches) == 0:
            logger.warning("TableSummary data batches is empty")
            yield {"table_summary": []}
        else:
            llm_results = await self.chain.ainvoke(data_batches)
            result = []
            for data_batch, llm_result in zip(data_batches, llm_results, strict=False):
                result.append(
                    {
                        "page": data_batch.get("page"),
                        "table_raw": data_batch.get("text"),
                        "table_summary": llm_result.content,
                    }
                )
            logger.debug(f"TableSummary result sample: {result[0]}")
            logger.info(f"TableSummary result length: {len(result)}")
            yield {"table_summary": result}
