from typing import Literal, TypedDict

from sqlalchemy.sql import ColumnElement

# reusable literal options
OrderDirection = Literal["asc", "desc"]
AvailableFields = Literal["id", "name", "created_at", "updated_at"] | str


class OrderByOption(TypedDict):
    field: AvailableFields
    direction: OrderDirection


from sqlalchemy import asc, desc
from sqlalchemy.orm import DeclarativeMeta


def get_order_by_clause(model: DeclarativeMeta, order: OrderByOption) -> ColumnElement:
    column = getattr(model, order["field"], None)
    if not column:
        raise ValueError(f"Invalid order field '{order['field']}' for {model.__name__}")
    return asc(column) if order["direction"] == "asc" else desc(column)
