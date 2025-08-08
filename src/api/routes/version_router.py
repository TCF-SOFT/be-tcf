import importlib.metadata

from fastapi import APIRouter

from src.config import settings
from src.utils.logging import logger

router = APIRouter(prefix="/-", tags=["Utils"])


@router.get("/version", response_model=dict, status_code=200)
async def api_microservice_version():
    """
    Returns microservice version.\f (from pyproject.toml)
    """
    version_number = None

    try:
        version_number = importlib.metadata.version(settings.PROJECT_NAME)
        logger.debug("Microservice version: %s", version_number)
    except Exception as e:
        logger.error(e)

    return {"version": version_number}
