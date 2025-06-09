import uuid

from fastapi import Request, BackgroundTasks
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.config.config import settings
from src.models.user import User
from src.utils.logging import logger
from tasks.mailing import send_verification_email


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.AUTH.RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = settings.AUTH.VERIFICATION_TOKEN_SECRET

    def __init__(
        self, user_db: SQLAlchemyUserDatabase, background_tasks: BackgroundTasks
    ):
        super().__init__(user_db)
        self.background_tasks = background_tasks

    async def on_after_register(self, user: User, request: Request | None = None):
        self.background_tasks.add_task(send_verification_email, user)
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
        logger.info("Email verification sent to user %r..", user.id)
        logger.warning(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )
