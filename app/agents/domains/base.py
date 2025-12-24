from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field

from app.agents.adaptor.llm_interface import ILLMAdapter
from app.agents.context.schema import (
    ROLE_TYPE,
    AgentState,
    Memory,
    Message,
)
from app.agents.interface import IAgent
from app.agents.sandbox.client import SANDBOX_CLIENT
from app.common.logger import logger


class BaseAgent(IAgent, BaseModel, ABC):
    """에이전트의 기본 뼈대를 정의하는 추상 클래스입니다.

    모든 에이전트가 공통으로 가져야 할 상태, 메모리, 실행 로직 등을 관리합니다.
    이 클래스를 상속받는 자식 클래스는 반드시 `step` 메서드를 구현해야 합니다.
    """

    # --- 핵심 속성 ---
    name: str = Field(
        ...,
        description="에이전트의 고유한 이름입니다. 에이전트를 식별하는 데 사용됩니다.",
    )
    description: str | None = Field(
        None, description="에이전트에 대한 간략한 설명입니다."
    )

    # --- 프롬프트 설정 ---
    system_prompt: str | None = Field(
        None,
        description="에이전트의 역할, 목표 등 전반적인 행동 지침을 정의하는 시스템 프롬프트입니다.",
    )
    next_step_prompt: str | None = Field(
        None, description="에이전트가 다음 행동을 결정할 때 참고하는 프롬프트입니다."
    )

    # --- 의존성 관리 ---
    llm: ILLMAdapter = Field(
        ILLMAdapter,
        description="에이전트가 사용할 언어 모델(LLM) 인스턴스입니다.",
    )
    memory: Memory = Field(
        default_factory=Memory,
        description="대화 기록을 저장하고 관리하는 메모리 모듈입니다.",
    )
    state: AgentState = Field(
        default=AgentState.IDLE,
        description="에이전트의 현재 상태(유휴, 실행 중, 완료, 오류)를 나타냅니다.",
    )

    # --- 실행 흐름 제어 ---
    max_steps: int = Field(
        default=10,
        description="에이전트가 무한 루프에 빠지는 것을 방지하기 위한 최대 실행 단계 수입니다.",
    )
    current_step: int = Field(
        default=0, description="현재까지 진행된 실행 단계 수입니다."
    )

    duplicate_threshold: int = 2

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # 자식 클래스에서 추가적인 필드를 유연하게 사용할 수 있도록 허용합니다.

    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """에이전트의 상태를 안전하게 변경하고 복원하기 위한 컨텍스트 관리자입니다.

        `with` 구문과 함께 사용되어 코드 블록 실행 전후로 상태를 관리합니다.

        예시:
            async with self.state_context(AgentState.RUNNING):
                # 이 블록 안에서는 에이전트 상태가 RUNNING이 됩니다.
                ...
            # 블록이 끝나면 이전 상태로 자동 복원됩니다.

        Args:
            new_state: 컨텍스트 블록 내에서 적용할 새로운 에이전트 상태.
        """
        if not isinstance(new_state, AgentState):
            raise ValueError(f"잘못된 상태 값입니다: {new_state}")

        previous_state = self.state
        self.state = new_state
        logger.debug(f"에이전트 상태 변경: {previous_state.value} -> {new_state.value}")
        try:
            yield
        except Exception as e:
            # 컨텍스트 블록 내에서 예외 발생 시 에이전트 상태를 ERROR로 변경합니다.
            logger.error(f"에이전트 실행 중 오류 발생: {e}")
            self.state = AgentState.ERROR
            raise e
        finally:
            # 컨텍스트 블록 실행이 끝나면(정상 종료 또는 예외 발생 모두), 이전 상태로 복원합니다.
            logger.debug(
                f"에이전트 상태 복원: {self.state.value} -> {previous_state.value}"
            )
            self.state = previous_state

    def update_memory(
        self,
        role: ROLE_TYPE,  # type: ignore
        content: str,
        base64_image: str | None = None,
        **kwargs,
    ) -> None:
        """에이전트의 단기 메모리(대화 기록)에 새로운 메시지를 추가합니다.

        Args:
            role: 메시지의 역할을 지정합니다 (예: 'user', 'assistant').
            content: 메시지의 내용입니다.
            base64_image: (선택) 메시지에 포함될 base64로 인코딩된 이미지입니다.
            **kwargs: (선택) 추가적인 메타데이터입니다 (예: tool_call_id).
        """
        message_map = {
            "user": Message.user_message,
            "system": Message.system_message,
            "assistant": Message.assistant_message,
            "tool": lambda content, **kw: Message.tool_message(content, **kw),
        }

        if role not in message_map:
            raise ValueError(f"지원하지 않는 메시지 역할입니다: {role}")

        # 역할에 따라 적절한 메시지 생성 메서드를 호출합니다.
        # 'tool' 역할의 경우, 'name'과 'tool_call_id' 같은 추가 인자가 필요할 수 있습니다.
        message_params = {"base64_image": base64_image}
        if role == "tool":
            message_params.update(kwargs)
            new_message = message_map[role](content, **message_params)
        else:
            new_message = message_map[role](content, **message_params)

        self.memory.add_message(new_message)
        logger.debug(
            f"단기 메모리에 메시지 추가됨: {new_message.role} - {content[:50]}..."
        )

    async def run(self, request: str | None = None) -> str:
        """에이전트의 전체 실행 사이클을 비동기적으로 처리합니다.

        'IDLE' 상태에서 시작하여 'RUNNING' 상태로 전환하고, 정해진 최대 단계(`max_steps`)까지 `step` 메서드를 반복 호출합니다.

        Args:
            request: (선택) 사용자의 초기 요청 메시지. 제공되면 대화의 시작점으로 메모리에 추가됩니다.

        Returns:
            에이전트 실행 완료 후 최종 결과 메시지.
        """
        if self.state != AgentState.IDLE:
            raise RuntimeError(
                f"에이전트는 'IDLE' 상태에서만 실행할 수 있습니다. 현재 상태: {self.state}"
            )

        if request:
            self.update_memory("user", request)

        results: list[str] = []
        async with self.state_context(AgentState.RUNNING):
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
            ):
                self.current_step += 1
                logger.info(f"--- 단계 {self.current_step}/{self.max_steps} 시작 ---")
                step_result = await self.step()

                # 에이전트가 비슷한 응답을 반복하며 루프에 빠졌는지 확인합니다.
                if self.is_stuck():
                    self.handle_stuck_state()

                results.append(f"단계 {self.current_step}: {step_result}")
                logger.info(
                    f"--- 단계 {self.current_step} 완료: {step_result[:100]}... ---"
                )

            if self.current_step >= self.max_steps:
                self.current_step = 0
                logger.warning(
                    f"최대 단계 수({self.max_steps})에 도달하여 실행을 종료합니다."
                )
                results.append(
                    f"실행 종료: 최대 단계 수({self.max_steps})에 도달했습니다."
                )
                # 상태는 state_context 관리자에 의해 IDLE로 자동 복원됩니다.

        await SANDBOX_CLIENT.cleanup()
        return "\n".join(results) if results else "실행된 단계가 없습니다."

    @abstractmethod
    async def step(self) -> str:
        """에이전트의 단일 행동 단계를 정의하는 추상 메서드입니다.

        자식 클래스에서 이 메서드를 반드시 구현하여 에이전트의 구체적인 행동 로직을 작성해야 합니다.
        (예: LLM 호출, 도구 사용 등)
        """

    def handle_stuck_state(self):
        """에이전트가 동일한 작업을 반복하는 '고착 상태'에 빠졌을 때 호출됩니다.

        전략을 바꾸도록 유도하는 프롬프트를 추가하여 문제를 해결하려고 시도합니다.
        """
        stuck_prompt = (
            "동일한 응답이 반복되고 있습니다. 이전과 다른 접근 방식을 시도하세요."
        )
        self.next_step_prompt = f"{stuck_prompt}\n{self.next_step_prompt}"
        logger.warning(
            "에이전트가 고착 상태에 빠진 것을 감지하고 전략 변경을 유도합니다."
        )

    def is_stuck(self) -> bool:
        """최근 대화 기록을 분석하여 에이전트가 동일한 응답을 반복하고 있는지 확인합니다.

        Returns:
            고착 상태이면 True, 아니면 False를 반환합니다.
        """
        # 메모리에 메시지가 충분히 쌓였는지 확인
        if len(self.memory.messages) < self.duplicate_threshold + 1:
            return False

        last_message = self.memory.messages[-1]
        # 마지막 메시지가 어시스턴트의 응답이 아니거나 내용이 없으면 확인할 필요가 없습니다.
        if last_message.role != "assistant" or not last_message.content:
            return False

        # 마지막 어시스턴트 응답과 동일한 내용의 이전 응답이 몇 번 있었는지 계산합니다.
        duplicate_count = sum(
            1
            for msg in self.memory.messages[-(self.duplicate_threshold + 1) : -1]
            if msg.role == "assistant" and msg.content == last_message.content
        )

        return duplicate_count >= self.duplicate_threshold

    @property
    def messages(self) -> list[Message]:
        """에이전트의 메모리에서 전체 메시지 목록을 가져옵니다."""
        return self.memory.messages

    @messages.setter
    def messages(self, value: list[Message]):
        """에이전트의 메모리에 전체 메시지 목록을 설정합니다."""
        self.memory.messages = value
