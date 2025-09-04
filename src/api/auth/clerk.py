import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions, RequestState
from fastapi import Depends, HTTPException, Request, status

from src.config import ServerEnv, settings
from src.schemas.common.enums import ROLE_HIERARCHY, Role
from src.schemas.webhooks.common import PublicMetadata

clerkClient = Clerk(bearer_auth=settings.AUTH.CLERK_SECRET_KEY)


async def require_clerk_session(
    request: Request,
) -> RequestState:
    """
    Проверяем JWT из Authorization: Bearer <token>.
    Вернём request_state, если пользователь действительно
    вошёл через Clerk, иначе бросим HTTP 401.
    """
    hx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=request.headers,
    )

    # Restriction for (authorized_parties) —
    # это защищает от токенов, выписанных для других доменов.
    if settings.SERVER.ENV == ServerEnv.TEST:
        state = clerkClient.authenticate_request(
            hx_request, AuthenticateRequestOptions()
        )
    else:
        state = clerkClient.authenticate_request(
            hx_request,
            AuthenticateRequestOptions(
                authorized_parties=settings.AUTH.AUTHORIZED_PARTIES
            ),
        )
    if not state.is_signed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthenticated: {state.reason}",
        )

    return state


def require_role(
    *allowed: Role,
):
    """
    Dependency factory for RBAC
    ADMIN > EMPLOYEE > USER
    """
    min_required = max(ROLE_HIERARCHY[r] for r in allowed)

    async def _dep(state: RequestState = Depends(require_clerk_session)) -> str:
        if settings.SERVER.ENV == ServerEnv.TEST:
            return settings.AUTH.TEST_EMPLOYEE_CLERK_ID
        else:
            clerk_id: str = state.payload.get("clerk_id")
            user = await clerkClient.users.get_async(user_id=clerk_id)
            public_md: PublicMetadata | dict = user.public_metadata
            user_role = public_md.get("_role")
            user_id = public_md.get("_id")

            if not user_role or ROLE_HIERARCHY.get(Role(user_role), 0) < min_required:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: role {user_role} is not allowed.",
                )
            return user_id

    return _dep
