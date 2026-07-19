from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_pipeline
from backend.models.api.response_models import ErrorResponse, JobStatusResponse, ReportResponse
from backend.pipeline.validation_pipeline import ValidationPipeline
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Jobs"])


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get Job Status",
    description="Returns the current status and progress of a validation job.",
    responses={
        404: {"description": "Job not found"},
    },
)
async def get_job_status(
    job_id: str,
    pipeline: ValidationPipeline = Depends(get_pipeline),
) -> JobStatusResponse:
    job = pipeline.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                code="JOB_NOT_FOUND",
                message=f"Job not found: {job_id}",
            ).model_dump(),
        )
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        current_stage=job.current_stage,
        completed_stages=job.completed_stages,
        remaining_stages=job.remaining_stages,
    )


@router.get(
    "/jobs/{job_id}/report",
    response_model=ReportResponse,
    summary="Get Job Report",
    description="Returns the validation report for a completed job.",
    responses={
        404: {"description": "Job not found"},
        409: {"description": "Report not ready - job is still running"},
    },
)
async def get_job_report(
    job_id: str,
    pipeline: ValidationPipeline = Depends(get_pipeline),
) -> ReportResponse:
    job = pipeline.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                code="JOB_NOT_FOUND",
                message=f"Job not found: {job_id}",
            ).model_dump(),
        )
    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                code="REPORT_NOT_READY",
                message=f"Job {job_id} is {job.status}, report not ready",
            ).model_dump(),
        )
    return ReportResponse(
        report=job.report.model_dump(mode="json") if job.report else None,
    )
