from typing import Any

from app.agents.context.schema import Message, Role
from app.agents.tools.utils.base import BaseTool
from app.common.logger import logger


class AskHumanTool(BaseTool):
    """작업 수행에 필요한 정보가 부족하거나 사용자의 의도가 모호할 때, 사용자에게 직접 질문하는 도구입니다."""

    name: str = "ask_human"
    description: str = (
        "작업을 계속 진행하기 전에 사용자로부터 추가 정보를 얻거나 모호함을 해소해야 할 때 사용합니다. "
        "다음과 같은 상황에 사용하십시오: "
        "1. **정보 부족**: 계획 수립이나 도구 사용에 필수적인 정보(예: 파일 이름, 검색 대상)가 누락되었을 때. "
        "2. **의도 모호**: 사용자의 요청이 여러 의미로 해석될 수 있어 명확한 방향 설정이 필요할 때. "
        "3. **중요 행동 확인**: 되돌릴 수 없는 중요한 행동(예: 파일 삭제, 데이터베이스 수정)을 수행하기 전 사용자에게 최종 확인을 받을 때."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "question_to_ask": {
                "type": "string",
                "description": "The specific, clear, and concise question to ask the user. The question should be phrased to elicit the exact information needed.",
            }
        },
        "required": ["question_to_ask"],
    }

    async def execute(self, question_to_ask: str, agent: Any, **kwargs) -> str:
        try:
            if agent.message_queue:
                await agent.message_queue.put(
                    Message(
                        role=Role.ASSISTANT,
                        content=question_to_ask,
                        metadata={"state": "assistant_finished"},
                    )
                )
            return f"사용자에게 {question_to_ask} 질문을 전달하였습니다."
        except Exception as e:
            error_msg = f"An error occurred during ask human tool execution: {e}"
            logger.exception(error_msg)
            return f"Error: {error_msg}"


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
        "properties": {
            "synthesis_brief": {
                "type": "string",
                "description": "Planner에 의해 최종적으로 종합된 결론과 핵심 정보. 이 브리핑에는 최종 답변 생성을 위한 모든 내용과 스타일 지침이 포함되어야 합니다.",
            }
        },
        "required": ["synthesis_brief"],
    }

    async def execute(self, synthesis_brief: str, agent: Any, **kwargs) -> str:
        try:
            logger.info("🔧 Executing answer tool 🔧 ")
            tool_msg = Message.tool_message(
                content="Executing answer tool to generate and stream the final response.",
                tool_call_id=agent.tool_calls[0].id,
                name=agent.tool_calls[0].function.name,
                base64_image=None,
            )
            agent.memory.add_message(tool_msg)

            # 최종 답변 생성을 위한 간단한 지시 프롬프트
            next_step_prompt = agent.tool_prompts.get(self.name, {}).get(
                "next_step_prompt", ""
            )
            if next_step_prompt:
                next_step_prompt = Message.user_message(
                    next_step_prompt.format(synthesis_brief=synthesis_brief)
                )
                agent.messages += [next_step_prompt]
            else:
                logger.warning("No next step prompt found for answer tool.")

            system_prompt = agent.tool_prompts.get(self.name, {}).get("system_prompt")
            if system_prompt:
                system_prompt = [Message.system_message(system_prompt)]
            else:
                system_prompt = []
                logger.warning("No system prompt found for answer tool.")

            final_content_buffer = ""
            async for chunk in agent.llm.ask_streaming(
                messages=agent.messages,
                system_msgs=system_prompt,
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
