from backend.agents.base_agent import StartupIQAgent
from backend.models.startup_profile import StartupProfile


class DiscoveryAgent(StartupIQAgent):
    name = "discovery"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        instructions = extra_instructions or [
            "Extract and normalize the startup information from the founder's responses.",
            "Ensure all required fields in the StartupProfile are populated.",
            "If information is missing, leave it as an empty string rather than fabricating it.",
        ]

        super().__init__(
            tools=tools,
            output_model=StartupProfile,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )
