from backend.agents.base_agent import StartupIQAgent
from backend.models.validation_plan import ValidationPlan


class PlannerAgent(StartupIQAgent):
    name = "planner"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        instructions = extra_instructions or [
            "Analyze the StartupProfile and determine the validation strategy.",
            "Identify which research categories are most relevant.",
            "Determine the appropriate research depth based on available information.",
            "Estimate completion time based on scope of validation required.",
        ]

        super().__init__(
            tools=tools,
            output_model=ValidationPlan,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
