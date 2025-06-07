from fastapi import APIRouter

from schemas.user_schema import UserCreate, UserRead
from src.api.auth.backend import authentication_backend
from src.api.routes.fastapi_users_router import fastapi_users_router

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

# /login
# /logout
router.include_router(
    router=fastapi_users_router.get_auth_router(authentication_backend),
)


# /register
router.include_router(
    router=fastapi_users_router.get_register_router(UserRead, UserCreate),
)
