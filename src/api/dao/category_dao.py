from api.dao.base import BaseDAO
from models.models import Category


class CategoryDAO(BaseDAO):
    model = Category
