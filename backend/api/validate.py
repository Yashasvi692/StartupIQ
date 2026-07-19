from fastapi import APIRouter, Depends

from backend.api.dependencies import get_pipeline
from backend.models.api.response_models import ValidateRequest, ValidateResponse
from backend.pipeline.validation_pipeline import ValidationPipeline
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Validation"])


@router.post(
    "/validate",
    status_code=202,
    response_model=ValidateResponse,
    summary="Create Validation Job",
    description="Creates a new validation job for the given startup profile.",
    responses={
        400: {"description": "Invalid input"},
    },
)
async def create_validation_job(
    body: ValidateRequest,
    pipeline: ValidationPipeline = Depends(get_pipeline),
) -> ValidateResponse:
    name = body.startup_profile.startup_name
    logger.info(f"POST /validate called for: {name} (mode={body.mode})")
    job = await pipeline.run_full_validation(
        body.startup_profile.model_dump(),
        mode=body.mode,
    )
    return ValidateResponse(job_id=job.job_id)
