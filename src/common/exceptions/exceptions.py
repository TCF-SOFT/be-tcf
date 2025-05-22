from fastapi import HTTPException, status


class DuplicateNameError(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with slug/name: '{name}' already exists.",
        )
