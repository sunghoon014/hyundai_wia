from app.agents.tools.utils.base import BaseTool


class CiteSources(BaseTool):
    """Provides structured citation data after generating the main answer."""

    name: str = "cite_sources"
    description: str = (
        "Use this tool to provide structured citation data for the information presented in the answer. "
        "This tool should be called AFTER the main text content has been fully generated. "
        "Do not write sources as plain text in the answer."
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "description": "A list of source objects used to generate the answer.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "The corresponding numerical marker in the text (e.g., 1, 2, 3).",
                        },
                        "url": {
                            "type": "string",
                            "description": "The URL of the source page or document.",
                        },
                        "tool_name": {
                            "type": "string",
                            "description": "retrieve_documents or web_search",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the source. if tool_name is retrieve_documents, it is the title of the document + page number",
                        },
                    },
                    "required": ["id", "url", "tool_name", "title"],
                },
            }
        },
        "required": ["sources"],
    }

    async def execute(self, sources: list[dict], **kwargs) -> list[dict]:
        """This tool's primary purpose is to transport data.

        The 'execute' method can simply return the sources.
        The client-side streaming handler will then process this structured data.
        """
        return sources
