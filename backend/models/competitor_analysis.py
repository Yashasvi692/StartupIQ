from pydantic import BaseModel, Field


class Competitor(BaseModel):
    name: str = Field(description="Competitor name")
    description: str = Field(default="", description="Brief description")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    pricing: str = Field(default="", description="Pricing model if known")
    market_share: str = Field(default="", description="Estimated market share")


class CompetitorAnalysis(BaseModel):
    direct_competitors: list[Competitor] = Field(default_factory=list)
    indirect_competitors: list[Competitor] = Field(default_factory=list)
    market_gaps: list[str] = Field(default_factory=list)
    differentiators: list[str] = Field(default_factory=list)
    competitive_threat_level: str = Field(
        default="unknown", description="Overall competitive threat"
    )
