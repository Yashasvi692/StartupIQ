from backend.agents.base_agent import StartupIQAgent
from backend.models.validation_report import ValidationReport


class ReportAgent(StartupIQAgent):
    name = "report"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        instructions = extra_instructions or [
            "Synthesize all research inputs into a comprehensive validation report.",
            "Generate all 15 report sections defined in the PRD specification.",
            "Build a validation scorecard with evidence-backed dimension scores.",
            "Pass through the original ResearchResult, CompetitorAnalysis, and BusinessFindings.",
            "Assign an overall validation score consistent with the scorecard.",
        ]

        super().__init__(
            tools=tools,
            output_model=ValidationReport,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
