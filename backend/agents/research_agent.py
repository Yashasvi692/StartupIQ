from backend.agents.base_agent import StartupIQAgent
from backend.models.research_result import ResearchResult
from backend.tools.duckduckgo_tool import DuckDuckGoTool


class ResearchAgent(StartupIQAgent):
    name = "research"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        if tools is None:
            tools = [DuckDuckGoTool()]

        instructions = extra_instructions or [
            "Use DuckDuckGo to search for publicly available information.",
            "Collect evidence from multiple sources when possible.",
            "Include supporting citations and source URLs for each finding.",
            "If no evidence is found, note the limitation rather than fabricating.",
        ]

        super().__init__(
            tools=tools,
            output_model=ResearchResult,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
