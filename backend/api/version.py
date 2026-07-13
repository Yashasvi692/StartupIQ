from fastapi import APIRouter

APP_VERSION = "1.0.0"
APP_NAME = "StartupIQ"

router = APIRouter()


@router.get("/version")
async def get_version():
    return {
        "project": APP_NAME,
        "version": APP_VERSION,
    }
