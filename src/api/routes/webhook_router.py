import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers.user_entity_controller import (
    create_user_entity,
    delete_user_entity,
    update_user_entity,
)
from api.di.db_helper import db_helper
from schemas.clerk_webhook_schema import ClerkWebhookSchema
from src.config import settings
from utils.logging import logger


def verify_clerk_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Hash-based Message Authentication Code (HMAC), is a cryptographic construction
    that uses a secret key and a cryptographic hash function to verify
    both the integrity and authenticity of a message
    """
    expected_signature = hmac.new(
        key=secret.encode(), msg=payload, digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/clerk/webhook",
    summary="Clerk Webhook Handler (user.created, user.deleted, user.updated)",
    status_code=200,
)
async def clerk_webhook(
    request: Request,
    clerk_signature: str = Header(
        None,
        alias="Clerk-Signature",
    ),
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    raw_body = await request.body()

    if not verify_clerk_signature(
        raw_body, clerk_signature, settings.AUTH.CLERK_SIGNING_SECRET
    ):
        raise HTTPException(status_code=401, detail="Invalid Clerk signature")

    payload: ClerkWebhookSchema = await request.json()
    logger.warning("[Clerk | Webhook] Event %s is caught", payload.type)

    if payload.type == "user.created":
        await create_user_entity(payload, db_session)

    elif payload.type == "user.updated":
        await update_user_entity(payload, db_session)

    elif payload.type == "user.deleted":
        await delete_user_entity(payload, db_session)
