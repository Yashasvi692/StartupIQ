from pydantic import BaseModel, Field


class Risk(BaseModel):
    risk: str = Field(description="Description of the risk")
    severity: str = Field(default="medium", description="Severity level")
    likelihood: str = Field(default="medium", description="Likelihood of occurrence")
    mitigation: str = Field(default="", description="Suggested mitigation")


class Opportunity(BaseModel):
    opportunity: str = Field(description="Description of the opportunity")
    priority: str = Field(default="medium", description="Priority level")


class SWOT(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    recommendation: str = Field(description="The recommendation")
    rationale: str = Field(default="", description="Why this recommendation")
    confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence score 0-1")


class BusinessFindings(BaseModel):
    swot: SWOT = Field(default_factory=SWOT)
    risks: list[Risk] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    business_model_evaluation: str = Field(
        default="", description="Evaluation of the business model"
    )
    strategic_recommendations: list[Recommendation] = Field(default_factory=list)
    validation_score: float = Field(
        default=0.0, ge=0, le=100, description="Overall validation score 0-100"
    )
