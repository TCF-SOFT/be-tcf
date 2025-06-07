from fastapi import APIRouter

from src.api.auth.backend import authentication_backend
from src.api.routes.fastapi_users_router import fastapi_users

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)