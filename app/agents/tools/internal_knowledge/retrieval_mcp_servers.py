"""Retrieval tools using Milvus vector store for document similarity search."""

import traceback
from dataclasses import dataclass

from fastmcp import FastMCP
from loguru import logger

from app.agents.tools.internal_knowledge.containers import RetrievalContainer

retrieval_mcp_server = FastMCP("Retrieval MCP Server")

retrieval_container = RetrievalContainer()
milvus_retriever = retrieval_container.milvus_retriever()


@dataclass
class DocumentMetadata:
    """Document metadata for retrieval with similarity score."""

    score: float
    id: str
    type: str
    title: str
    url: str
    page_num: str
    summary: str


@dataclass
class DocumentResult:
    """Document result for retrieval with similarity score."""

    page_content: str
    metadata: DocumentMetadata
    score: float


@dataclass
class RetrievalResult:
    """Result of document retrieval with scores."""

    query: str
    documents: list[DocumentResult]
    count: int


@retrieval_mcp_server.tool(
    name="retrieve_documents",
    description=(
        "Retrieves documents similar to a query from the Milvus vector store. "
        "IMPORTANT: Do not use the user's short query as-is. "
        "To improve search accuracy, analyze the conversational context and rephrase or expand the query into a more detailed and informative 'Search Query'. "
    ),
)
async def retrieve_documents(query: str, collection_name: str) -> RetrievalResult:
    """Retrieve documents similar to the query from the vector store.

    Args:
        query: The search query to find similar documents
        collection_name: The name of Milvus collection to search in

    Returns:
        Dictionary containing list of similar documents
    """
    try:
        search_results = await milvus_retriever.hybrid_search(
            query, collection_name=collection_name
        )
        if not search_results:
            logger.warning(f"No documents found for query: {query}")

        formatted_docs = [
            DocumentResult(
                page_content=result.doc.page_content,
                metadata=result.doc.metadata,
                score=result.score,
            )
            for result in search_results
        ]

        result = RetrievalResult(
            query=query, documents=formatted_docs, count=len(formatted_docs)
        )

        return result
    except Exception as e:
        raise Exception(f"Error retrieving documents: {traceback.format_exc()}") from e
