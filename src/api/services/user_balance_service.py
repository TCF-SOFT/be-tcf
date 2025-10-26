from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.user_balance_history_dao import UserBalanceHistoryDAO
from src.api.dao.user_dao import UserDAO
from src.models import User
from src.schemas.common.enums import Currency, UserBalanceChangeReason
from src.schemas.user_balance_history import UserBalanceHistoryPostSchema


class UserBalanceService:
    @staticmethod
    async def change_balance(
        db_session: AsyncSession,
        user_id: UUID,
        delta: float,
        reason: UserBalanceChangeReason,
        currency: Currency = Currency.RUB,
        waybill_id: UUID | None = None,
    ) -> None:
        """
        Change user balance and create history record.
        """
        user: User | None = await UserDAO.find_by_id(db_session, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        before = user.balance_rub
        after = before + delta
        user.balance_rub = after

        db_session.add(user)  # add user update to session

        history = UserBalanceHistoryPostSchema(
            user_id=user_id,
            waybill_id=waybill_id,
            delta=delta,
            currency=currency,
            balance_before=before,
            balance_after=after,
            reason=reason,
        )

        return await UserBalanceHistoryDAO.add(db_session, **history.model_dump())
