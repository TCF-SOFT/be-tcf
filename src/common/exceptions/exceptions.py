from fastapi import HTTPException, status


class DuplicateSlugError(HTTPException):
    def __init__(self, slug: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with slug: '{slug}' already exists.",
        )
