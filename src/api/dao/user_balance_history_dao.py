from src.api.dao.base import BaseDAO
from src.models import UserBalanceHistory
from src.schemas.user_balance_history import UserBalanceHistorySchema


class UserBalanceHistoryDAO(BaseDAO):
    model = UserBalanceHistory
    schema = UserBalanceHistorySchema
