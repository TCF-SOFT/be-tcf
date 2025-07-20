from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from svix import Webhook, exceptions

from src.api.controllers.user_entity_controller import (
    create_user_entity,
    delete_user_entity,
    update_user_entity,
)
from src.api.di.db_helper import db_helper
from src.config import settings
from src.schemas.clerk_webhook_schema import ClerkWebhookSchema
from src.utils.logging import logger


def verify_clerk_signature(
    payload,
    headers: dict[str, str],
    secret: str,
) -> bool:
    """
    Hash-based Message Authentication Code (HMAC)
    """
    wh = Webhook(secret)
    try:
        wh.verify(payload, headers)
        return True
    except (
        exceptions.WebhookVerificationError,
        exceptions.HTTPValidationError,
        exceptions.HttpError,
    ) as e:
        logger.error("[Clerk | Webhook] Signature verification failed: %s", e)
        return False


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/clerk",
    summary="Clerk Webhook Handler (user.created, user.deleted, user.updated)",
    status_code=200,
)
async def clerk_webhook(
    request: Request,
    svix_signature: str = Header(
        None,
        alias="svix-signature",
    ),
    svix_id: str = Header(
        None,
        alias="svix-id",
    ),
    svix_timestamp: str = Header(
        None,
        alias="svix-timestamp",
    ),
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    raw_body = await request.body()
    headers = {
        "svix-signature": svix_signature,
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
    }
    if not verify_clerk_signature(
        raw_body, headers, settings.AUTH.CLERK_SIGNING_SECRET
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
