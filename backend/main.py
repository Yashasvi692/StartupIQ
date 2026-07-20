from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import api_router
from backend.pipeline.validation_pipeline import ValidationPipeline
from backend.utils.config import settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.pipeline = ValidationPipeline()
    yield


app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
