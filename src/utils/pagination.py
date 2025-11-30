from typing import TypeVar

from fastapi import Query
from fastapi_pagination import Page
from fastapi_pagination.customization import CustomizedPage, UseParamsFields

T = TypeVar("T")

Page = CustomizedPage[
    Page[T],
    UseParamsFields(
        # change default size 50 -> 300, increase upper limit to 500
        size=Query(300, ge=1, le=500),
    ),
]
