import uuid

from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers

from src.api.auth.backend import authentication_backend
from src.api.auth.dependencies import get_user_manager
from src.models import User

fastapi_users_router = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [authentication_backend],
)

current_active_user = fastapi_users_router.current_user(active=True)
current_active_superuser = fastapi_users_router.current_user(
    active=True, superuser=True
)


def require_admin(user: User = Depends(current_active_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    return user


def require_employee(user: User = Depends(current_active_user)):
    if user.role != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    return user
