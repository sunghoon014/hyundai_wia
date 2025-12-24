from app.agents.domains.ax.consulting import ConsultingAgent
from app.agents.domains.kearney.kearney import KearneyAgent

AGENT_REGISTRY = {
    "kearney": KearneyAgent,
    "ax": ConsultingAgent,
}
