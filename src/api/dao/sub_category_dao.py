from src.api.dao.base import BaseDAO
from src.models import SubCategory
from src.schemas.sub_category_schema import SubCategorySchema


class SubCategoryDAO(BaseDAO):
    model = SubCategory
    schema = SubCategorySchema
