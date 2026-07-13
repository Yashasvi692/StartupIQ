from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.health import router as health_router
from backend.api.version import router as version_router
from backend.utils.config import settings

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(version_router)
