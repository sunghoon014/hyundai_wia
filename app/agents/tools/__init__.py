from app.agents.tools.utils.ask_human import AnswerTool, AskHumanTool
from app.agents.tools.utils.planning import PlanningTool
from app.agents.tools.utils.source import CiteSources
from app.agents.tools.utils.terminate import (
    AnswerWithCiteSourcesStreamingTool,
    AnswerWithCiteSourcesTool,
)

# is_special ture는 호출 후 에이전트 실행을 종료.
TOOL_REGISTRY = {
    "cite_sources": {
        "class": CiteSources,
        "is_special": True,
    },
    "ask_human": {
        "class": AskHumanTool,
        "is_special": True,
    },
    "answer": {
        "class": AnswerTool,
        "is_special": True,
    },
    "answer_with_cite_sources": {
        "class": AnswerWithCiteSourcesTool,
        "is_special": True,
    },
    "answer_with_cite_sources_streaming": {
        "class": AnswerWithCiteSourcesStreamingTool,
        "is_special": True,
    },
    "planning": {
        "class": PlanningTool,
        "is_special": False,
    },
}
