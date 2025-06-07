import uuid

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from models.user import User
from src.config.config import settings
from src.utils.logging import logger


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.AUTH.RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = settings.AUTH.VERIFICATION_TOKEN_SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.warning(
            "User %r has registered.",
            user.id,
        )

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.warning(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.warning(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )
