from pydantic import BaseModel


class CategoryFacet(BaseModel):
    category_slug: str
    product_count: int


class SubCategoryFacet(BaseModel):
    sub_category_slug: str
    product_count: int


class ProductFacetsSchema(BaseModel):
    categories: list[CategoryFacet]
    sub_categories: list[SubCategoryFacet]
