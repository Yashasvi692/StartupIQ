from fastapi import APIRouter

from backend.utils.config import settings

router = APIRouter()


@router.get("/version")
async def get_version():
    return {
        "project": settings.project_name,
        "version": settings.project_version,
    }
