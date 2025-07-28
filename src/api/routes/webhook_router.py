from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from svix import Webhook, exceptions

from src.api.auth.clerk import clerkClient
from src.api.controllers.user_entity_controller import (
    create_user_entity,
    delete_user_entity,
    update_user_entity,
)
from src.api.di.db_helper import db_helper
from src.config import settings
from src.schemas.webhooks.clerk_webhook_schema import UserWebhookSchema
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
    response_model=dict,
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
    raw_body: bytes = await request.body()
    raw_json: dict = await request.json()
    headers = {
        "svix-signature": svix_signature,
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
    }
    if not verify_clerk_signature(
        raw_body, headers, settings.AUTH.CLERK_SIGNING_SECRET
    ):
        raise HTTPException(status_code=401, detail="Invalid Clerk signature")

    payload: UserWebhookSchema = UserWebhookSchema.model_validate(raw_json)
    logger.warning("[ClerkWebhook] Event %s is caught", raw_json)

    if payload.type == "user.created":
        await create_user_entity(payload, db_session, clerkClient)
        return {"message": "User created successfully"}

    elif payload.type == "user.updated":
        await update_user_entity(payload, db_session)
        return {"message": "User updated successfully"}

    elif payload.type == "user.deleted":
        await delete_user_entity(payload, db_session)
        return {"message": "User deleted successfully"}

    else:
        logger.error("[ClerkWebhook] Unsupported event type: %s", payload.type)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported event type"
        )
