import base64
from functools import lru_cache
from uuid import UUID

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import Depends, Header, HTTPException, Request, status
from jwt import (
    ExpiredSignatureError,
    PyJWTError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.audit_log import save_log_entry
from src.api.dao.user_dao import UserDAO
from src.api.di.db_helper import db_helper
from src.config import settings
from src.schemas.common.enums import ROLE_HIERARCHY, Role
from src.schemas.user_schema import UserSchema


@lru_cache()
def load_jwks():
    """
    GET http://localhost:3000/api/auth/jwks
    {
      "keys":[
        {
          "alg":"EdDSA",
          "crv":"Ed25519",
          "x":"XemzE1yUJr3l96kqDR9XgH0Y4s0s_YpjHgg6CCYbJIc",
          "kty":"OKP",
          "kid":"d73eac0c-f0b4-4443-978e-a75935bc2d70"
        }
      ]
    }
    """
    resp = httpx.get(settings.AUTH.JWKS_URL, timeout=5)
    if resp.status_code != 200:
        raise RuntimeError("JWKS endpoint returned non‑200")
    jwks = resp.json().get("keys", [])
    if not jwks:
        raise RuntimeError("JWKS endpoint returned no keys")
    return jwks


def get_ed25519_key(jwk_dict: dict) -> Ed25519PublicKey:
    # проверяем тип и кривую, как требует спецификация OKP/EdDSA:contentReference[oaicite:3]{index=3}
    if jwk_dict.get("kty") != "OKP" or jwk_dict.get("crv") != "Ed25519":
        raise ValueError("JWK is not an Ed25519 key")
    x_b64 = jwk_dict.get("x")
    if not x_b64:
        raise ValueError("Missing x in JWK")
    # декодируем base64url (добавляем паддинг, если его нет)
    x_bytes = base64.urlsafe_b64decode(x_b64 + "==")
    return Ed25519PublicKey.from_public_bytes(x_bytes)


def verify_better_auth_jwt(token: str) -> dict:
    # Get unverified header to extract kid
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed JWT header"
        )
    kid = header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing kid in JWT"
        )

    # search JWK by kid
    jwks = load_jwks()
    jwk_dict = next((k for k in jwks if k.get("kid") == kid), None)
    if jwk_dict is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key"
        )

    # строим Ed25519 public key
    public_key = get_ed25519_key(jwk_dict)

    decode_kwargs: dict = {
        "key": public_key,
        "algorithms": ["EdDSA"],
        "options": {
            "require": ["sub", "iat", "exp"],
            "verify_iss": False,
            "verify_aud": False,
        },
    }

    try:
        # logger.info(f"Verifying JWT token: {token}")
        payload = jwt.decode(token, **decode_kwargs)
        iss = payload.get("iss")
        aud = payload.get("aud")

        if not iss or iss not in settings.AUTH.BETTER_AUTH_ISSUERS:
            raise HTTPException(status_code=401, detail="Invalid issuer")
        if not aud or aud not in settings.AUTH.BETTER_AUTH_AUDIENCES:
            raise HTTPException(status_code=401, detail="Invalid audience")

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid JWT")

    return payload


async def require_better_auth_session(
    authorization: str | None = Header(None),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    token = authorization.split(" ", 1)[1]
    return verify_better_auth_jwt(token)


def require_role(
    *allowed: Role,
):
    """
    Dependency factory for RBAC
    ADMIN > EMPLOYEE > USER
    """
    min_required = max(ROLE_HIERARCHY[r] for r in allowed)

    async def _dep(
        request: Request,
        db_session: AsyncSession = Depends(db_helper.session_getter),
        state: dict = Depends(require_better_auth_session),
    ) -> str:
        user_raw = await UserDAO.find_by_id(db_session, UUID(state["sub"]))

        if not user_raw:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        user = UserSchema.model_validate(user_raw)

        if ROLE_HIERARCHY.get(Role(user.role), 0) < min_required:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role {user.role} is not allowed.",
            )

        if user.role == Role.EMPLOYEE or user.role == Role.ADMIN:
            await save_log_entry(db_session, user.id, request)

        return str(user.id)

    return _dep
