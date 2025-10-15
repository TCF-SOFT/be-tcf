from src.api.dao.base import BaseDAO
from src.models import UserBalanceHistory


class UserBalanceHistoryDAO(BaseDAO):
    model = UserBalanceHistory
