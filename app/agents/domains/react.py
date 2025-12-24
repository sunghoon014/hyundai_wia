from abc import ABC, abstractmethod

from app.agents.domains.base import BaseAgent


class ReActAgent(BaseAgent, ABC):
    """ReAct (Reason + Act) 프레임워크를 구현하는 에이전트의 추상 기본 클래스입니다.

    ReAct는 언어 모델이 '생각(Reason)' 단계를 통해 행동 계획을 수립하고, '행동(Act)' 단계를 통해 도구를 사용하거나 응답을 생성하는 과정을 반복하도록 합니다.
    이 클래스는 `think`와 `act`라는 두 개의 핵심 추상 메서드를 정의하여 자식 클래스에서 구체적인 ReAct 로직을 구현하도록 강제합니다.
    """

    @abstractmethod
    async def think(self) -> bool:
        """'생각(Reason)' 단계를 수행합니다.

        현재 대화 상태(메모리)를 분석하여 다음에 어떤 행동을 할지 결정합니다.
        - 어떤 도구를 사용할지
        - 사용자에게 어떤 질문을 할지
        - 최종 답변을 생성할지 등을 결정합니다.

        Returns:
            행동(act)을 수행해야 하면 True, 그렇지 않으면 False를 반환합니다.
        """

    @abstractmethod
    async def act(self) -> str:
        """'행동(Act)' 단계를 수행합니다.

        `think` 단계에서 결정된 계획에 따라 실제 행동을 실행합니다.
        - 도구를 사용하고 그 결과를 반환합니다.
        - 최종 답변을 생성하여 반환합니다.

        Returns:
            행동 수행 결과를 담은 문자열을 반환합니다.
        """

    async def step(self) -> str:
        """ReAct 에이전트의 단일 실행 단계를 정의합니다.

        `think()`를 호출하여 계획을 세우고, 그 결과에 따라 `act()`를 호출하여 행동합니다.
        """
        should_act = await self.think()
        if not should_act:
            return "생각 완료 - 추가 행동 필요 없음"
        return await self.act()
