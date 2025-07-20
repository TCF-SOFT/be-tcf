from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.base import BaseDAO
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

    @classmethod
    async def delete_by_clerk_id(cls, db_session: AsyncSession, clerk_id: str) -> bool:
        """
        Try to delete a row by clerk_id.

        Returns:
            True  – if record existed and was removed
            False – if record not found
        """
        stmt = (
            sa_delete(cls.model)
            .where(cls.model.clerk_id == clerk_id)
            .returning(cls.model.clerk_id)  # ← return clerk_id of deleted row
        )

        result = await db_session.execute(stmt)
        await db_session.flush()

        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None
