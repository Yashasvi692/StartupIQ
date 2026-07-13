from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    category: str = Field(
        description=(
            "Category: missing_section, unsupported_recommendation, "
            "missing_citation, formatting_issue, missing_confidence"
        )
    )
    description: str = Field(description="Detailed description of the issue")
    severity: str = Field(
        default="medium",
        description="Severity: low, medium, high, critical",
    )
    section: str = Field(
        default="",
        description="The report section where the issue was found",
    )


class ReviewResult(BaseModel):
    issues: list[ReviewIssue] = Field(default_factory=list)
    overall_quality_score: float = Field(
        default=100.0, ge=0, le=100, description="Overall quality score 0-100"
    )
    passed: bool = Field(default=True, description="Whether the report passes quality review")
    summary: str = Field(default="", description="Summary of the review findings")
