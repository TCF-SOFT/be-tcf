from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.user_manager import UserManager
from src.api.di.database import get_db
from src.models.access_token import AccessToken
from src.models.user import User


async def get_users_db(db_session: AsyncSession = Depends(get_db)):
    """
    Dependency to get the User database adapter.
    """
    return User.get_db(db_session)


async def get_access_tokens_db(db_session: AsyncSession = Depends(get_db)):
    """
    Dependency to get the Access Token database adapter.
    """
    return AccessToken.get_db(db_session)


async def get_user_manager(users_db=Depends(get_users_db)):
    yield UserManager(users_db)
