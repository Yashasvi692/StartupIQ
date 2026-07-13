from typing import Any

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any = None


class ErrorResponse(BaseModel):
    status: str = "error"
    code: str = Field(description="Error code identifier")
    message: str = Field(description="Human-readable error description")
    details: dict[str, Any] = Field(default_factory=dict)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str = Field(description="Job status (queued/running/completed/failed/cancelled)")
    progress: int = Field(default=0, ge=0, le=100)
    current_stage: str = ""
    completed_stages: list[str] = Field(default_factory=list)
    remaining_stages: list[str] = Field(default_factory=list)
