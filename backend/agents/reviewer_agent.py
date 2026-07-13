from backend.agents.base_agent import StartupIQAgent
from backend.models.review_result import ReviewResult


class ReviewerAgent(StartupIQAgent):
    name = "review"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        instructions = extra_instructions or [
            "Review the ValidationReport for quality issues.",
            "Check for missing report sections.",
            "Identify unsupported recommendations.",
            "Detect missing citations in evidence-backed claims.",
            "Verify formatting consistency across sections.",
            "Ensure confidence scores are present in the scorecard.",
            "Assign an overall quality score and pass/fail decision.",
        ]

        super().__init__(
            tools=tools,
            output_model=ReviewResult,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
