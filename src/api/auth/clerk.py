import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions, RequestState
from fastapi import HTTPException, Request, status

from src.config import settings

clerk = Clerk(bearer_auth=settings.AUTH.CLERK_SECRET_KEY)


async def require_clerk_session(request: Request) -> RequestState:
    """
    Проверяем JWT из Authorization: Bearer <token>.
    Вернём request_state, если пользователь действительно
    вошёл через Clerk, иначе бросим HTTP 401.
    """
    hx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=request.headers,  # <-- содержат Authorization
    )

    # Можно дополнительно ограничить aud (authorized_parties) —
    # это защищает от токенов, выписанных для других доменов.
    state = clerk.authenticate_request(
        hx_request,
        AuthenticateRequestOptions(authorized_parties=settings.AUTH.AUTHORIZED_PARTIES),
    )

    if not state.is_signed_in:
        # state.reason содержит причину (expired, invalid_signature…)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthenticated: {state.reason}",
        )

    return state
