import importlib.metadata

from src.config.config import settings
from src.utils.logging import logger


async def get_microservice_version() -> str:
    """Returns microservice version from pyproject.toml"""

    version_number = None

    try:
        version_number = importlib.metadata.version(settings.PROJECT_NAME)
        logger.debug("Microservice version: %s", version_number)
    except Exception as e:
        logger.error(e)

    return version_number
