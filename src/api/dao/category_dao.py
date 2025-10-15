from src.api.dao.base import BaseDAO
from src.models import Category
from src.schemas.category_schema import CategorySchema


class CategoryDAO(BaseDAO):
    model = Category
    schema = CategorySchema
