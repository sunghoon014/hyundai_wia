from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph, StateGraph

from app.common.logger import logger
from app.domains.document.enums import DocumentProcessingStatus
from app.domains.document.handlers.langchain.adapter import LangchainAdapter
from app.domains.document.handlers.langchain.chain import summarize_chain
from app.domains.document.handlers.langchain.parser import parse_with_langchain
from app.domains.document.handlers.node.base import BaseNode
from app.domains.document.handlers.node.utils import (
    continue_parse,
    download_file_to_firebase_url,
)
from app.domains.document.schemas.state import ParseState


class ParsingService:
    """Parsing 서비스 클래스입니다.

    Knowledge Center에 업로드 할 문서를 파싱하고, 파싱 결과를 몽고 디비에 저장하거나 RAG를 위한 문서 객체를 생성합니다.
    """

    def __init__(
        self,
        split_pdf_files_node: BaseNode,
        upstage_parse_node: BaseNode,
        post_parse_node: BaseNode,
        working_queue_node: BaseNode,
        page_summary_node: BaseNode,
        image_summary_node: BaseNode,
        table_summary_node: BaseNode,
        langchain_document_node: BaseNode,
        langchain_adapter: LangchainAdapter,
    ):
        self.split_pdf_files_node = split_pdf_files_node
        self.upstage_parse_node = upstage_parse_node
        self.post_parse_node = post_parse_node
        self.working_queue_node = working_queue_node
        self.page_summary_node = page_summary_node
        self.image_summary_node = image_summary_node
        self.table_summary_node = table_summary_node
        self.langchain_document_node = langchain_document_node
        self.langchain_adapter = langchain_adapter

    def _create_graph(self) -> CompiledStateGraph:
        """LangGraph를 빌드하고 컴파일합니다.

        추후 동적으로 node를 선택할 수 있도록 구현하면 좋겠으나, 현재 구현 방식에서는 어려움이 있음
        """
        state_graph = StateGraph(ParseState)

        logger.info("Adding nodes to graph...")
        state_graph.add_node("split_pdf_files_node", self.split_pdf_files_node.execute)
        state_graph.add_node("upstage_parse_node", self.upstage_parse_node.execute)
        state_graph.add_node("post_parse_node", self.post_parse_node.execute)
        state_graph.add_node("working_queue_node", self.working_queue_node.execute)
        state_graph.add_node("page_summary_node", self.page_summary_node.execute)
        state_graph.add_node("image_summary_node", self.image_summary_node.execute)
        state_graph.add_node("table_summary_node", self.table_summary_node.execute)
        state_graph.add_node(
            "langchain_document_node", self.langchain_document_node.execute
        )

        logger.info("Adding edges to graph...")
        state_graph.add_edge("split_pdf_files_node", "working_queue_node")
        # OCR 경로
        state_graph.add_conditional_edges(
            "working_queue_node",
            continue_parse,
            {True: "upstage_parse_node", False: "post_parse_node"},
        )  # 큐가 비면 post_ocr_node로 이동
        state_graph.add_edge("upstage_parse_node", "working_queue_node")
        state_graph.add_edge("post_parse_node", "page_summary_node")
        state_graph.add_edge("post_parse_node", "image_summary_node")
        state_graph.add_edge("post_parse_node", "table_summary_node")
        state_graph.add_edge("page_summary_node", "langchain_document_node")
        state_graph.add_edge("image_summary_node", "langchain_document_node")
        state_graph.add_edge("table_summary_node", "langchain_document_node")

        state_graph.set_entry_point("split_pdf_files_node")  # 시작노드 지정

        logger.info("Compiling graph...")
        # TODO: MemorySavers는 in-memory 저장 방식이라 서비스 단에서 사용하기 어려움 / Redis(from langgraph.checkpoint.redis import RedisCheckpointer) 등 영속성 체크포인터 고려 필요
        compiled_graph = state_graph.compile(checkpointer=MemorySaver())
        # mermaid_definition = compiled_graph.get_graph(xray=True).draw_mermaid()
        # logger.info(f"mermaid_definition:\n{mermaid_definition}")
        # logger.info("Graph compiled successfully.")
        # exit()

        return compiled_graph

    async def _astream(
        self,
        graph: CompiledStateGraph,
        inputs: dict,
        config: dict | None = None,
        stream_mode: str = "messages",
        include_subgraphs: bool = False,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """LangGraph의 실행 결과를 비동기적으로 스트리밍하고 직접 출력하는 함수.

        Args:
            graph: 컴파일된 LangGraph 인스턴스
            inputs: 입력 데이터
            config: 구성 정보
            node_names: 스트리밍할 노드 이름 리스트
            callback: 콜백 함수
            stream_mode: 스트리밍 모드 (messages 또는 updates)
            include_subgraphs: 서브그래프 포함 여부

        Returns:
            최종 결과 딕셔너리
        """
        config = config or {}
        if stream_mode == "messages":
            async for chunk, metadata in graph.astream(
                inputs, config, stream_mode=stream_mode
            ):
                curr_node = metadata.get("langgraph_node", "")

                # 노드에서 yield한 로그/결과를 그대로 content로 전달
                out = {"node": curr_node, "content": chunk, "metadata": metadata}
                logger.info(f"\n🔄 Completed Node: {curr_node} 🔄\n{'- '*25}")
                yield out

        elif stream_mode == "updates":
            async for chunk in graph.astream(
                inputs, config, stream_mode=stream_mode, subgraphs=include_subgraphs
            ):
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    namespace, node_chunks = chunk
                else:
                    namespace, node_chunks = (), chunk

                if isinstance(node_chunks, dict):
                    for node_name, node_chunk in node_chunks.items():
                        logger.info(f"\n🔄 Completed Node: {node_name} 🔄\n{'- '*25}")
                        # 각 노드별로 내부 처리 상태를 상세하게 안내하는 메시지
                        if node_name == "split_pdf_files_node":
                            out = {
                                "node": node_name,
                                "role": DocumentProcessingStatus.PARSING.status,
                                "percentage": 5,
                                "content": (
                                    "The system is downloading the file and splitting it into individual pages. "
                                    "This step prepares the document for further analysis and enables efficient processing of large files."
                                ),
                            }
                            yield out
                        elif node_name == "upstage_parse_node":
                            out = {
                                "node": node_name,
                                "role": DocumentProcessingStatus.PARSING.status,
                                "percentage": 30,
                                "content": (
                                    "The system is analyzing the document structure and extracting various elements such as images, tables, and text blocks. "
                                    "This process identifies and separates different content types to enable specialized handling in subsequent steps."
                                ),
                            }
                            yield out
                        elif node_name == "page_summary_node":
                            out = {
                                "node": node_name,
                                "role": DocumentProcessingStatus.PREPROCESSING.status,
                                "percentage": 60,
                                "content": (
                                    "The system is generating concise summaries for each page. "
                                    "Key information and main ideas are being extracted to facilitate downstream tasks such as search and question answering."
                                ),
                            }
                            yield out
                        elif node_name == "langchain_document_node":
                            out = {
                                "node": node_name,
                                "role": DocumentProcessingStatus.PREPROCESSING.status,
                                "percentage": 80,
                                "content": (
                                    "The system is chunking the document into smaller segments optimized for retrieval-augmented generation (RAG) and semantic search. "
                                    "Each chunk is enriched with metadata to support efficient and accurate information retrieval."
                                ),
                            }
                            yield out

    async def parse_document(
        self,
        document_url: str,
        file_name: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """PDFs, DOCX, TXT, CSV, Excel, etc."""
        ext = file_name.split(".")[-1].lower()
        if ext in ["pdf", "docx", "xlsx", "pdf", "jpg", "jpeg", "hwp", "hwpx", "pptx"]:
            app = self._create_graph()
            config = RunnableConfig(
                recursion_limit=50,
                max_concurrency=50,
                configurable={"thread_id": "1"},
            )
            inputs = ParseState(
                ext=ext,
                filepath=document_url,
                file_name=file_name,
                save_dir="./data",
            )

            # 워크플로우 중간 과정 스트리밍
            async for chunk in self._astream(app, inputs, config, "updates"):
                yield chunk

            # 최종 상태 반환
            state = app.get_state(config)
            yield {
                "node": "final_state",
                "title": file_name,
                "summary": state.values.get("document_summary"),
                "content": state.values.get("documents"),
                "document_url": document_url,
            }
        else:
            temp_file_path = None
            yield {
                "node": "text_loader_node",
                "role": DocumentProcessingStatus.PARSING.status,
                "percentage": 30,
                "content": f"The system is downloading the file: {file_name} ...",
            }
            if document_url.startswith(("http://", "https://")):
                temp_file_path = await download_file_to_firebase_url(
                    document_url, f"./data/tmp/{file_name}"
                )

            yield {
                "node": "text_loader_node",
                "role": DocumentProcessingStatus.PARSING.status,
                "percentage": 60,
                "content": (
                    "The system is chunking the document into smaller segments optimized for retrieval-augmented generation (RAG) and semantic search. "
                    "Each chunk is enriched with metadata to support efficient and accurate information retrieval."
                ),
            }
            docs = await parse_with_langchain(
                path=temp_file_path if temp_file_path else document_url,
                ext=ext,
                file_name=file_name,
            )
            yield {
                "node": "text_loader_node",
                "role": DocumentProcessingStatus.PREPROCESSING.status,
                "percentage": 80,
                "content": (
                    "The system is generating concise summaries for each page. "
                    "Key information and main ideas are being extracted to facilitate downstream tasks such as search and question answering."
                ),
            }
            logger.info(f"Created {len(docs)} langchain documents")
            summary = await summarize_chain(
                documents=docs[0], adapter=self.langchain_adapter
            )
            logger.info(f"File {file_name} summary: {summary.content}")
            yield {
                "node": "final_state",
                "title": file_name,
                "summary": summary.content,
                "content": docs,
                "document_url": document_url,
            }
