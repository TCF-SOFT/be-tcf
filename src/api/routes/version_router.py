from fastapi import APIRouter

from src.api.controllers.api_microservice_version import get_microservice_version

router = APIRouter(prefix="/-", tags=["Utils"])


@router.get("/version", response_model=dict, status_code=200)
async def api_microservice_version() -> dict:
    """Returns microservice version from pyproject.toml"""
    version = await get_microservice_version()
    return {"version": version}
