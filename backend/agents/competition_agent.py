from pydantic import BaseModel

from backend.agents.base_agent import StartupIQAgent
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.utils.logger import get_logger
from backend.workflows.deterministic_search import DeterministicSearch

logger = get_logger(__name__)

PLANNING_PROMPT_TEMPLATE = (
    "Based on the startup context below, generate up to {max_queries} "
    "specific DuckDuckGo search queries that will help identify competitors for this startup's "
    "industry, including both direct and indirect competitors.\n"
    "Return only the list of search queries.\n\n"
    "Startup Context:\n{context}"
)


class CompetitionAgent(StartupIQAgent):
    name = "competition"

    def __init__(
        self,
        tools: list | None = None,
        llm_config=None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
    ) -> None:
        instructions = extra_instructions or [
            "Identify direct and indirect competitors.",
            "Compare product features, pricing, and positioning.",
            "Identify market gaps and potential differentiators.",
            "Assess the overall competitive threat level.",
        ]

        super().__init__(
            tools=[],
            output_model=CompetitorAnalysis,
            llm_config=llm_config,
            markdown=markdown,
            extra_instructions=instructions,
        )

        self._search = DeterministicSearch()

    async def run_structured(
        self,
        message: str,
        output_model: type[BaseModel] | None = None,
    ) -> BaseModel:
        model = output_model or self._output_model
        if model is None:
            raise ValueError(
                "No output model set. Pass output_model to run_structured() "
                "or provide it in the constructor."
            )

        planning_prompt = PLANNING_PROMPT_TEMPLATE.format(
            max_queries=self._search.max_queries,
            context=message,
        )

        return await self._search.run(
            agent=self.agent,
            context=message,
            planning_prompt=planning_prompt,
            output_model=model,
            agent_name=self.name,
        )
