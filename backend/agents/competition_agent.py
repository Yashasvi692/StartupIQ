from backend.agents.base_agent import StartupIQAgent
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.tools.duckduckgo_tool import DuckDuckGoTool


class CompetitionAgent(StartupIQAgent):
    name = "competition"

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
            "Search for competitors using DuckDuckGo.",
            "Identify direct and indirect competitors.",
            "Compare product features, pricing, and positioning.",
            "Identify market gaps and potential differentiators.",
            "Assess the overall competitive threat level.",
        ]

        super().__init__(
            tools=tools,
            output_model=CompetitorAnalysis,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
