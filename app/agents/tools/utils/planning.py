from typing import Any

from app.agents.context.schema import Message
from app.agents.tools.utils.base import BaseTool
from app.common.logger import logger


class PlanningTool(BaseTool):
    """A tool that analyzes the user's request and the conversation state to create a structured plan for the agent to follow."""

    name: str = "planning"
    description: str = "사용자의 요청이 모호하거나, 여러 단계의 작업이 필요하거나, 전략적인 분석이 필요할 때 호출됩니다. 가능하면 항상 계획을 먼저 세우는 것이 가장 안전합니다."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "context_or_query": {
                "type": "string",
                "description": "The user's latest query and any relevant context for planning.",
            }
        },
        "required": ["context_or_query"],
    }

    async def execute(self, context_or_query: str, agent: Any, **kwargs) -> str:
        """Executes the final answer streaming process using the agent's context.

        This method is designed to be called with the agent instance itself as an argument.

        Args:
            context_or_query: The user's latest query and any relevant context for planning.
            agent: The instance of the agent executing this tool. It needs access to
                   agent.llm, agent.messages, agent.message_queue, etc.
            **kwargs: Additional arguments for the tool.

        Returns:
            A string indicating the result of the operation.
        """
        try:
            logger.info("🔧 Executing planning tool 🔧 ")
            tool_msg = Message.tool_message(
                content="Executing planning tool to create a structured plan for the next action.",
                tool_call_id=agent.tool_calls[0].id,
                name=agent.tool_calls[0].function.name,
            )
            temp_messages = agent.messages + [tool_msg]

            next_step_prompt = agent.tool_prompts.get(self.name, {}).get(
                "next_step_prompt", ""
            )
            if next_step_prompt:
                next_step_prompt = Message.user_message(
                    next_step_prompt.format(context_or_query=context_or_query)
                )
                temp_messages += [next_step_prompt]
            else:
                logger.warning("No next step prompt found for planning tool.")
                temp_messages += [Message.user_message(context_or_query)]

            system_prompt = agent.tool_prompts.get(self.name, {}).get("system_prompt")
            system_prompt = (
                [Message.system_message(system_prompt)] if system_prompt else []
            )
            if not system_prompt:
                logger.warning("No system prompt found for planning tool.")

            response = await agent.llm.ask(
                messages=temp_messages,
                system_msgs=system_prompt,
            )

            if agent.message_queue:
                await agent.message_queue.put(
                    Message.assistant_message(
                        content=response,
                        metadata={"state": "assistant_running"},
                    )
                )

            return response
        except Exception as e:
            error_msg = f"An error occurred during planning: {e}"
            logger.exception(error_msg)
            return f"Error: {error_msg}"
