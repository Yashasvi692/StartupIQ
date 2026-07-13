from datetime import datetime

from pydantic import BaseModel, Field

from backend.models.business_findings import BusinessFindings
from backend.models.competitor_analysis import CompetitorAnalysis
from backend.models.research_result import ResearchResult


class DimensionScore(BaseModel):
    score: float = Field(ge=0, le=100, description="Score 0-100")
    explanation: str = Field(default="")
    evidence: str = Field(default="")
    confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence score 0-1")


class ValidationReport(BaseModel):
    executive_summary: str = Field(default="")
    startup_snapshot: str = Field(default="")
    problem_analysis: str = Field(default="")
    market_analysis: str = Field(default="")
    industry_trends: str = Field(default="")
    competitor_landscape: str = Field(default="")
    customer_validation: str = Field(default="")
    business_model_evaluation: str = Field(default="")
    technical_feasibility: str = Field(default="")
    swot_analysis: str = Field(default="")
    risk_assessment: str = Field(default="")

    validation_scorecard: dict[str, DimensionScore] = Field(default_factory=dict)
    strategic_recommendations: list[str] = Field(default_factory=list)
    suggested_next_steps: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)

    research_result: ResearchResult | None = None
    competitor_analysis: CompetitorAnalysis | None = None
    business_findings: BusinessFindings | None = None

    overall_score: float = Field(default=0.0, ge=0, le=100)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
