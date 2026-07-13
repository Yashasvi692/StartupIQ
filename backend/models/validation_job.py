from datetime import datetime

from pydantic import BaseModel, Field

from backend.models.startup_profile import StartupProfile
from backend.models.validation_report import ValidationReport


class ValidationJob(BaseModel):
    job_id: str = Field(description="Unique job identifier")
    status: str = Field(default="queued", description="Job status")
    mode: str = Field(default="deep", description="Validation mode (quick/deep)")

    startup_profile: StartupProfile = Field(description="The startup profile")
    report: ValidationReport | None = Field(default=None, description="Generated report")

    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    current_stage: str = Field(default="Discovery", description="Current pipeline stage")
    completed_stages: list[str] = Field(default_factory=list)
    remaining_stages: list[str] = Field(default_factory=list)

    error_message: str | None = Field(default=None, description="Error message if failed")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)
