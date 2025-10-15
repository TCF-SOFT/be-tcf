from src.api.dao.base import BaseDAO
from src.models import Category


class CategoryDAO(BaseDAO):
    model = Category
