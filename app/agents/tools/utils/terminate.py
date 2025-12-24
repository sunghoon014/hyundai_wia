import asyncio
import json
import re
from typing import Any

from app.agents.context.schema import AgentState, Message, Role
from app.agents.tools.utils.base import BaseTool
from app.agents.tools.utils.source import CiteSources
from app.agents.tools.utils.tool_collection import ToolCollection
from app.common.logger import logger

_TERMINATE_DESCRIPTION = """Terminate the interaction when the request is met OR if the assistant cannot proceed further with the task. When you have finished all the tasks, call this tool to end the work."""


class Terminate(BaseTool):
    name: str = "terminate"
    description: str = _TERMINATE_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "The finish status of the interaction.",
                "enum": ["success", "failure"],
            }
        },
        "required": ["status"],
    }

    async def execute(self, status: str, **kwargs) -> str:
        """Finish the current execution."""
        logger.info(f"Terminate tool executed with status: {status}")
        return f"The interaction has been completed with status: {status}"


class AnswerTool(BaseTool):
    """A tool for delivering direct, non-sourced answers to the user.

    Used for conversational replies or to report search failures.
    """

    name: str = "answer"
    description: str = (
        "사용자에게 직접 텍스트 답변을 전달합니다. 이 도구는 검색 결과나 외부 자료를 인용하지 않으며, "
        "다음과 같은 경우에 사용됩니다: "
        "1. 단순한 인사, 감사 등 일반적인 대화에 응답할 때. "
        "2. 모든 작업이 완료된 후, 최종 결론이나 요약 내용을 전달할 때. "
        "3. 사용자에게 시스템의 상태나 작업 실패 사실을 알려야 할 때."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def execute(self, agent: Any, **kwargs) -> str:
        """Executes the final answer streaming process using the agent's context.

        This method is designed to be called with the agent instance itself as an argument.

        Args:
            agent: The instance of the agent executing this tool. It needs access to
                   agent.llm, agent.messages, agent.message_queue, etc.
            **kwargs: Additional arguments for the tool.

        Returns:
            A string indicating the result of the operation.
        """
        try:
            tool_msg = Message.tool_message(
                content="Executing answer to generate and stream the final response.",
                tool_call_id=agent.tool_calls[0].id,
                name=agent.tool_calls[0].function.name,
                base64_image=None,
            )
            agent.memory.add_message(tool_msg)

            # 최종 답변 생성을 위한 간단한 지시 프롬프트
            next_step_prompt = agent.tool_prompts.get(self.name, {}).get(
                "next_step_prompt", ""
            )
            next_step_prompt = Message.user_message(next_step_prompt)
            agent.messages += [next_step_prompt]

            system_prompt = agent.tool_prompts.get(self.name, {}).get("system_prompt")
            system_prompt = (
                [Message.system_message(system_prompt)] if system_prompt else []
            )
            if not system_prompt:
                logger.warning("No system prompt found for answer tool.")

            final_content_buffer = ""
            async for chunk in agent.llm.ask_tool_streaming(
                messages=agent.messages,
                system_msgs=system_prompt,
                tools=None,
            ):
                delta = chunk.choices[0].delta
                if delta.content:
                    content = delta.content
                    final_content_buffer += content
                    if agent.message_queue:
                        await agent.message_queue.put(
                            Message(
                                role=Role.ASSISTANT,
                                content=content,
                                metadata={"state": "assistant_streaming"},
                            )
                        )

            # 스트리밍 종료 후 메모리에 최종 답변 저장 및 종료 신호 전송
            agent.memory.add_message(Message.assistant_message(final_content_buffer))
            if agent.message_queue:
                await agent.message_queue.put(
                    Message(
                        role=Role.ASSISTANT,
                        content=final_content_buffer,
                        metadata={"state": "assistant_finished"},
                    )
                )
            return "Final answer has been successfully streamed to the user."
        except Exception as e:
            error_msg = f"An error occurred during final answer streaming: {e}"
            logger.exception(error_msg)
            return f"Error: {error_msg}"


class AnswerWithCiteSourcesTool(BaseTool):
    """A special tool that is called when the agent has gathered all necessary information and is ready to provide the complete, final answer to the user.

    Executing this tool triggers the final, streaming response to the user.
    """

    name: str = "answer_with_cite_sources"
    description: str = (
        "Previously gathered search results (`retrieve`, `web_search`) are synthesized to generate the final answer with source citations like [1], [2]. "
        "**WHEN TO USE:** Call this tool ONLY when: "
        "1. You have already successfully called `retrieve` or `web_search`. "
        "2. You have evaluated the search results and have confirmed they are SUFFICIENT and RELEVANT to the user's question. "
        "**WHEN NOT TO USE:** Do NOT call this if no search was performed or if the search results were insufficient. In those cases, use the `answer` tool instead to ask the user for clarification."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def execute(self, agent: Any, **kwargs) -> str:
        """Executes the final answer streaming process using the agent's context.

        This method is designed to be called with the agent instance itself as an argument.

        Args:
            agent: The instance of the agent executing this tool. It needs access to
                   agent.llm, agent.messages, agent.message_queue, etc.
            **kwargs: Additional arguments for the tool.

        Returns:
            A string indicating the result of the operation.
        """
        # NOTE: This method is a placeholder for actual planning logic
        if agent.message_queue:
            await agent.message_queue.put(
                Message.assistant_message(
                    content="I've gathered the key pieces of information. Now, I'm structuring and writing the final answer for you... ✨",
                    metadata={"state": AgentState.RUNNING.value},
                )
            )
        tool_msg = Message.tool_message(
            content="Executing answer_with_cite_sources to generate and stream the final response.",
            tool_call_id=agent.tool_calls[0].id,
            name=agent.tool_calls[0].function.name,
            base64_image=None,
        )
        agent.memory.add_message(tool_msg)

        next_step_prompt = agent.tool_prompts.get(self.name, {}).get("next_step_prompt")
        if not next_step_prompt:
            logger.warning(
                "No next step prompt found for answer_with_cite_sources tool."
            )
        next_step_prompt = Message.user_message(next_step_prompt)
        agent.messages += [next_step_prompt]

        system_prompt = agent.tool_prompts.get(self.name, {}).get("system_prompt")
        system_prompt = [Message.system_message(system_prompt)] if system_prompt else []
        if not system_prompt:
            logger.warning("No system prompt found for answer_with_cite_sources tool.")

        # streaming answer
        final_answer = await agent.llm.ask(
            messages=agent.messages, system_msgs=system_prompt
        )

        # JSON 파싱: --- 뒤의 JSON 부분을 추출하고 파싱
        sources_json = None
        if "---" in final_answer:
            # --- 이후의 텍스트를 분리
            parts = final_answer.split("---", 1)
            if len(parts) > 1:
                json_part = parts[1].strip()

                # 정규식으로 ```json``` 블록에서 JSON 추출 시도, 없으면 원본 사용
                match = re.search(r"```json\s*([\s\S]*?)\s*```", json_part)
                json_content = match.group(1).strip() if match else json_part.strip()

                # JSON 파싱 시도
                if json_content:
                    try:
                        sources_json = json.loads(json_content)
                        logger.info(
                            f"[AnswerWithCiteSourcesTool] Parsed sources JSON: {sources_json}"
                        )
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"[AnswerWithCiteSourcesTool] Failed to parse JSON: {e}"
                        )

        # 스트리밍용 답변에서 --- JSON 부분 제거 (깔끔한 사용자 경험을 위해)
        streaming_answer = (
            final_answer.split("---")[0].strip()
            if "---" in final_answer
            else final_answer
        )

        # 처음 10개의 토큰(단어)을 스트리밍으로 하나씩 내보내고, 나머지는 한 번에 출력하도록 구현
        tokens = streaming_answer.split(" ")
        stream_count = min(10, len(tokens))  # 10개 토큰만 스트리밍
        # 앞부분 토큰을 하나씩 스트리밍
        for i in range(stream_count):
            await agent.message_queue.put(
                Message.assistant_message(
                    content=tokens[i] + " ",
                    metadata={"state": "assistant_streaming"},
                )
            )
            await asyncio.sleep(0.01)
        # 나머지 토큰을 한 번에 출력
        if len(tokens) > stream_count:
            rest = " ".join(tokens[stream_count:])
            await agent.message_queue.put(
                Message.assistant_message(
                    content=rest, metadata={"state": "assistant_streaming"}
                )
            )

        # 파싱된 소스 정보를 메시지 큐에 추가
        if sources_json and agent.message_queue:
            for source in sources_json:
                if source.get("tool_name") in [
                    "retrieve_documents",
                    "retrieve",
                    "mcp_retrieval_retrieve_documents",
                    "mcp_retrieval",
                    "mcp_retrieval_retrieve",
                    "mcp_retrieval_documents",
                ]:
                    link_type = "doc_link"
                else:
                    link_type = "web_link"
                # role must be 'assistant' for source chunks
                await agent.message_queue.put(
                    Message.assistant_message(
                        content=str(source),
                        metadata={"state": link_type},
                    )
                )
        # 메모리에는 원본 답변 저장 (JSON 포함)
        final_answer_msg = Message.assistant_message(final_answer)
        agent.memory.add_message(final_answer_msg)
        agent.messages += [final_answer_msg]

        # 종료 신호에는 스트리밍용 답변만 포함
        await agent.message_queue.put(
            Message.assistant_message(
                content=streaming_answer,
                metadata={"state": AgentState.FINISHED.value},
            )
        )
        return "Final answer has been successfully streamed to the user."


class AnswerWithCiteSourcesStreamingTool(BaseTool):
    """A special tool that is called when the agent has gathered all necessary information.

    Executing this tool triggers the final, streaming response to the user.
    """

    name: str = "answer_with_cite_sources_streaming"
    description: str = (
        "Call this tool ONLY when you have gathered all necessary information and are ready to "
        "provide the complete, final answer to the user. This signals the end of the reasoning process."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def execute(self, agent: Any, **kwargs) -> str:
        """Executes the final answer streaming process using the agent's context.

        This method is designed to be called with the agent instance itself as an argument.

        Args:
            agent: The instance of the agent executing this tool. It needs access to
                   agent.llm, agent.messages, agent.message_queue, etc.
            **kwargs: Additional arguments for the tool.

        Returns:
            A string indicating the result of the operation.
        """
        if agent.message_queue:
            await agent.message_queue.put(
                Message(
                    role=Role.ASSISTANT,
                    content="I've gathered the key pieces of information. Now, I'm structuring and writing the final answer for you... ✨",
                    metadata={"state": "assistant_running"},
                )
            )
        tool_msg = Message.tool_message(
            content="Executing FinalAnswerTool to generate and stream the final response.",
            tool_call_id=agent.tool_calls[0].id,
            name=agent.tool_calls[0].function.name,
            base64_image=None,
        )
        agent.memory.add_message(tool_msg)
        next_step_prompt = agent.tool_prompts.get(self.name, {}).get("next_step_prompt")
        # 최종 답변 생성을 위한 간단한 지시 프롬프트
        next_step_prompt = Message.user_message(next_step_prompt)
        agent.messages += [next_step_prompt]

        system_prompt = agent.tool_prompts.get(self.name, {}).get("system_prompt")
        system_prompt = [Message.system_message(system_prompt)] if system_prompt else []
        if not system_prompt:
            logger.warning(
                "No system prompt found for answer_with_cite_sources_streaming tool."
            )

        final_tool_calls = {}
        final_content_buffer = ""
        available_tools = ToolCollection(CiteSources())
        try:
            async for chunk in agent.llm.ask_tool_streaming(
                messages=agent.messages,
                system_msgs=system_prompt,
                tools=available_tools.to_params(),
                tool_choice=agent.tool_choices,
            ):
                delta = chunk.choices[0].delta

                # Tool Call 처리
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        index = tool_call.index
                        if index not in final_tool_calls:
                            final_tool_calls[index] = tool_call
                        else:
                            final_tool_calls[
                                index
                            ].function.arguments += tool_call.function.arguments
                # 일반 텍스트 답변 스트리밍 처리
                if delta.content:
                    content = delta.content
                    final_content_buffer += content
                    if agent.message_queue:
                        await agent.message_queue.put(
                            Message(
                                role=Role.ASSISTANT,
                                content=content,
                                metadata={"state": "assistant_streaming"},
                            )
                        )

            # 스트리밍이 모두 끝난 후
            for _, tool_call in final_tool_calls.items():
                if tool_call.function.name == "cite_sources":
                    # JSON 문자열 인자를 파싱
                    source_data = json.loads(tool_call.function.arguments)
                    if agent.message_queue and source_data:
                        for source in source_data["sources"]:
                            if source["tool_name"] == "retrieve_documents":
                                link_type = "doc_link"
                            else:
                                link_type = "web_link"

                            await agent.message_queue.put(
                                Message.assistant_message(
                                    content=str(source),
                                    metadata={"state": link_type},
                                )
                            )

            # 스트리밍 종료 후 메모리에 최종 답변 저장 및 종료 신호 전송
            agent.state = AgentState.FINISHED
            agent.memory.add_message(Message.assistant_message(final_content_buffer))
            if agent.message_queue:
                await agent.message_queue.put(
                    Message.assistant_message(
                        content=final_content_buffer,
                        metadata={"state": AgentState.FINISHED.value},
                    )
                )
            return "Final answer has been successfully streamed to the user."
        except Exception as e:
            error_msg = f"An error occurred during final answer streaming: {e}"
            logger.exception(error_msg)
            return f"Error: {error_msg}"
