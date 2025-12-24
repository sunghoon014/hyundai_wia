from functools import partial
from typing import Any

from langchain_core.runnables import RunnableLambda

from app.domains.document.handlers.langchain.adapter import LangchainAdapter


async def _extract_page_summary(
    data_batches: list[dict[str, Any]], adapter: LangchainAdapter
) -> list[Any]:
    system_prompts = []
    user_prompts = []
    for data_batch in data_batches:
        system_prompt = data_batch.get("system_prompt", "")
        system_prompts.append(system_prompt)

        text = data_batch.get("text", "")
        user_prompt = f"# CONTEXT:\n{text}"
        user_prompts.append(user_prompt)

    answers = await adapter.llm_client_abatch(
        system_prompts=system_prompts, user_prompts=user_prompts
    )
    return answers


def get_extract_page_summary_runnable(
    adapter: LangchainAdapter,
) -> RunnableLambda:
    bound_async_logic = partial(_extract_page_summary, adapter=adapter)
    return RunnableLambda(bound_async_logic)


async def _extract_document_summary(
    datas: list[dict[str, Any]], adapter: LangchainAdapter
) -> str:
    system_prompt = datas[0].get("system_prompt", "")
    text = ""
    for data in datas:
        text += data.get("page_summary", "")

    user_prompt = f"# CONTEXT:\n{text}"

    answer = await adapter.llm_client_ainvoke(
        system_prompt=system_prompt, user_prompt=user_prompt
    )
    return answer


def get_extract_document_summary_runnable(
    adapter: LangchainAdapter,
) -> RunnableLambda:
    bound_async_logic = partial(_extract_document_summary, adapter=adapter)
    return RunnableLambda(bound_async_logic)


async def _extract_image_summary(
    data_batches: list[dict[str, Any]], adapter: LangchainAdapter
) -> list[Any]:
    system_prompts = []
    user_prompts = []
    image_inputs = []
    mime_types = []
    for data_batch in data_batches:
        system_prompt = data_batch.get("system_prompt", "")
        system_prompts.append(system_prompt)

        text = data_batch.get("text", "")
        user_prompt = f"# Related Context:\n{text}"
        user_prompts.append(user_prompt)

        image_input = data_batch.get("base64_encoding", "")
        image_inputs.append(image_input)

        mime_type = data_batch.get("mime_type", "")
        mime_types.append(mime_type)

    answers = await adapter.multi_modal_client_abatch(
        image_inputs=image_inputs,
        system_prompts=system_prompts,
        user_prompts=user_prompts,
        mime_types=mime_types,
    )
    return answers


def get_extract_image_summary_runnable(
    adapter: LangchainAdapter,
) -> RunnableLambda:
    bound_async_logic = partial(_extract_image_summary, adapter=adapter)
    return RunnableLambda(bound_async_logic)


async def _extract_table_summary(
    data_batches: list[dict[str, Any]], adapter: LangchainAdapter
) -> list[Any]:
    system_prompts = []
    user_prompts = []
    image_inputs = []
    mime_types = []
    for data_batch in data_batches:
        system_prompt = data_batch.get("system_prompt", "")
        system_prompts.append(system_prompt)

        text = data_batch.get("text", "")
        user_prompt = f"# Related Context:\n{text}"
        user_prompts.append(user_prompt)

        image_input = data_batch.get("base64_encoding", "")
        image_inputs.append(image_input)

        mime_type = data_batch.get("mime_type", "")
        mime_types.append(mime_type)

    answers = await adapter.multi_modal_client_abatch(
        image_inputs=image_inputs,
        system_prompts=system_prompts,
        user_prompts=user_prompts,
        mime_types=mime_types,
    )
    return answers


def get_extract_table_summary_runnable(
    adapter: LangchainAdapter,
) -> RunnableLambda:
    bound_async_logic = partial(_extract_table_summary, adapter=adapter)
    return RunnableLambda(bound_async_logic)


async def summarize_chain(
    adapter: LangchainAdapter, documents: list[str] | None = None
) -> str:
    system_prompt = """# Role & Goal
You are a Document Synthesis Analyst. Your mission is to take a collection of individual page summaries and synthesize them into a single, coherent, and highly-discoverable data package.

# Workflow
1.  **Document Overview:** Write a one-line summary that captures the core essence of the document.
2.  **Keyword Generation:** Create a list of 3-5 strategic keywords that would help a user find this document in a large database.
3.  **Hypothetical Questions:** Formulate 3-5 distinct questions that a user might ask about the document. These questions must be answerable using only the document's information present.

# Output Format
Present your complete analysis in the following structured format. Do not add any text outside of this structure.

<one_line_summary>
[one_line_summary]
</one_line_summary>
<keywords>
[keywords]
</keywords>
<hypothetical_questions>
[hypothetical_questions]
</hypothetical_questions>"""
    user_prompt = f"# CONTEXT:\n{documents}"
    answer = await adapter.llm_client_ainvoke(
        system_prompt=system_prompt, user_prompt=user_prompt
    )
    return answer
