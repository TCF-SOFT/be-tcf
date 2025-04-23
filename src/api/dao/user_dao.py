from api.dao.base import BaseDAO
from models.models import User


class UserDAO(BaseDAO):
    model = User
