from sqlalchemy.ext.asyncio import AsyncSession

from api.dao.base import BaseDAO
from src.models.user import User


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_by_clerk_id(
        cls, db_session: AsyncSession, clerk_id: str
    ) -> User | None:
        """
        Find a user by their clerk ID.
        """
        return await cls.find_one_or_none(db_session, {"clerk_id": clerk_id})
