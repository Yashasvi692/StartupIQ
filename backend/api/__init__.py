from fastapi import APIRouter

from backend.api.health import router as health_router
from backend.api.jobs import router as jobs_router
from backend.api.validate import router as validate_router
from backend.api.version import router as version_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(validate_router)
api_router.include_router(version_router)
