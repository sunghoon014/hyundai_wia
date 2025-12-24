from pydantic import Field

from app.agents.adaptor.llm_interface import ILLMAdapter
from app.agents.context.schema import AgentState, Message
from app.agents.domains.ax.toolcall import ToolCallAgent
from app.agents.tools import TOOL_REGISTRY
from app.common.logger import logger
from app.common.messaging.message_queue import MessageQueue


class ConsultingAgent(ToolCallAgent):
    name: str = "Consulting"
    description: str = (
        "컨설팅 에이전트는 컨설팅팀의 내부 프로세스를 자동화 하기 위한 에이전트 입니다."
    )

    max_observe: int = 10000
    max_steps: int = 10

    tool_prompts: dict[str, str] = Field(
        default_factory=dict,
        description="도구 호출 시 사용할 프롬프트 딕셔너리입니다.",
    )

    @classmethod
    async def create(
        cls,
        llm: ILLMAdapter,
        agent_setup: dict[str, str] = None,
        **kwargs,
    ) -> "ConsultingAgent":
        """에이전트 인스턴스를 생성하고 비동기적으로 초기화하는 팩토리 메서드입니다.

        직접 생성자를 호출하는 대신 이 메서드를 사용하는 것이 안전합니다.
        """
        instance = cls(llm=llm, **kwargs)
        # 프롬프트 설정
        prompt_dict = agent_setup.get("prompt_dict", {})
        instance.system_prompt = prompt_dict.get("system_prompt", "")
        instance.next_step_prompt = prompt_dict.get("next_step_prompt", "")
        instance.tool_prompts = prompt_dict.get("tool_prompts", {})

        # 도구 설정
        tool_list = agent_setup.get("tool_list", [])
        for tool_name in tool_list:
            tool_config = TOOL_REGISTRY[tool_name]
            tool_class = tool_config["class"]
            is_special = tool_config["is_special"]
            instance.available_tools.add_tools(tool_class())
            if is_special:
                instance.special_tool_names.append(tool_name)

        return instance

    async def cleanup(self):
        """에이전트 실행이 끝난 후 관련 리소스(메모리 등)를 정리합니다."""
        self.memory.clear()
        await super().cleanup()

    async def think(self) -> bool:
        """에이전트의 '생각' 과정을 담당하는 핵심 메서드입니다.

        상황(LLM 모델, 에이전트 모드 등)에 맞춰 적절한 `think` 로직을 호출합니다.
        """
        return await super().think()

    async def _handle_special_tool(self, name: str, result: str, **kwargs):
        """'FinalAnswer'처럼 에이전트의 실행을 종료시키는 특별한 도구의 호출을 처리합니다.

        해당 도구가 호출되면 에이전트의 상태를 'FINISHED'로 변경합니다.
        """
        if not self._is_special_tool(name):
            return

        if self._should_finish_execution(name=name, result=result, **kwargs):
            logger.info(f"특별 도구 '{name}'가 작업을 완료하여 실행을 종료합니다.")
            self.state = AgentState.FINISHED

    async def run_with_sse(self, message_queue: MessageQueue) -> str:
        """SSE(Server-Sent Events)를 통해 실시간으로 진행 상황을 클라이언트에 전달하며 에이전트를 실행합니다.

        클라이언트는 이 메서드를 통해 에이전트의 각 단계를 스트리밍으로 받을 수 있습니다.

        Args:
            message_queue: 클라이언트로 메시지를 전송하기 위한 큐.

        Returns:
            에이전트 실행 완료 후 최종 결과 메시지.
        """
        if self.state != AgentState.IDLE:
            raise RuntimeError(
                f"에이전트는 'IDLE' 상태에서만 실행할 수 있습니다. 현재 상태: {self.state}"
            )
        logger.info(f"ConsultingAgent Memory length: {len(self.memory.messages)}")
        self.message_queue = message_queue
        async with self.state_context(AgentState.RUNNING):
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
            ):
                self.current_step += 1
                logger.info(
                    f"----------------------- 단계 {self.current_step} 시작 -----------------------"
                )
                await self.step()

                if self.is_stuck():
                    self.handle_stuck_state()
                    logger.info(
                        f"반복적인 동작이 감지되어 전략을 수정합니다. \n{self.next_step_prompt}"
                    )

                logger.info(
                    f"----------------------- 단계 {self.current_step} 완료 -----------------------"
                )

            # --- 실행 종료 처리 ---
            if self.current_step >= self.max_steps:
                logger.warning(
                    f"최대 단계 수({self.max_steps})에 도달하여 실행을 종료합니다."
                )
                if self.message_queue:
                    # 사용자에게 상황을 알리는 메시지를 전송합니다.
                    await self.message_queue.put(
                        Message.assistant_message(
                            content="더 깊이 탐색했지만, 명확한 답변을 찾기 어렵습니다. 요청을 조금 더 구체적으로 말씀해주시겠어요?",
                            metadata={"state": "assistant_streaming"},
                        )
                    )

        # 에이전트 실행이 모두 끝나면 리소스를 정리합니다.
        await self.cleanup()
        logger.info("에이전트 실행이 모두 종료되었습니다.")
