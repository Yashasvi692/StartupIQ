from pydantic import BaseModel, Field


class ValidationPlan(BaseModel):
    research_depth: str = Field(description="Depth of research required (quick/deep)")
    required_agents: list[str] = Field(description="Agents needed for this validation")
    execution_strategy: str = Field(description="Strategy for executing validation")
    estimated_completion_seconds: int = Field(description="Estimated time in seconds")
    research_categories: list[str] = Field(
        default_factory=list, description="Research categories to analyze"
    )
