from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.config import settings

header_scheme = APIKeyHeader(name="api-key")


def validate_api_key(api_key: str = Depends(header_scheme)) -> None:
    if api_key != settings.AUTH.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return None
