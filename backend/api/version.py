from fastapi import APIRouter

from backend.models.api.response_models import VersionResponse
from backend.utils.config import settings

router = APIRouter(tags=["System"])


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Get Version",
    description="Returns the project name and version.",
)
async def get_version() -> VersionResponse:
    return VersionResponse(
        project=settings.project_name,
        version=settings.project_version,
    )
