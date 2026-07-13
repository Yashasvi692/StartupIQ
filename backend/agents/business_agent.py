from backend.agents.base_agent import StartupIQAgent
from backend.models.business_findings import BusinessFindings


class BusinessAgent(StartupIQAgent):
    name = "business"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        instructions = extra_instructions or [
            "Analyze the StartupProfile, ResearchResult, and CompetitorAnalysis.",
            "Perform SWOT analysis based on collected evidence.",
            "Identify risks with severity and likelihood assessments.",
            "Identify opportunities with priority levels.",
            "Evaluate the business model and provide a validation score.",
            "Generate strategic recommendations with supporting rationale.",
        ]

        super().__init__(
            tools=tools,
            output_model=BusinessFindings,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
