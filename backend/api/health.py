from fastapi import APIRouter

from backend.models.api.response_models import HealthResponse

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the backend health status.",
)
async def health_check() -> HealthResponse:
    return HealthResponse()
