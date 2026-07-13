from pydantic import BaseModel, Field


class ResearchFinding(BaseModel):
    finding: str = Field(description="The research finding")
    source: str = Field(default="", description="Source of the finding")
    confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence score 0-1")


class ResearchResult(BaseModel):
    market_size_findings: list[ResearchFinding] = Field(default_factory=list)
    industry_trends: list[ResearchFinding] = Field(default_factory=list)
    customer_pain_points: list[ResearchFinding] = Field(default_factory=list)
    technology_landscape: list[ResearchFinding] = Field(default_factory=list)
    additional_findings: list[ResearchFinding] = Field(default_factory=list)
