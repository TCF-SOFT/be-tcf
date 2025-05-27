from api.dao.base import BaseDAO
from src.models.models import User


class UserDAO(BaseDAO):
    model = User
