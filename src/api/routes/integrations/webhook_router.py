from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.utils import verify_signature
from src.schemas.webhooks import BetterAuthWebhookSchema
from src.api.auth.clerk import clerkClient
from src.api.core.user_entity import (
    create_user_entity,
    delete_user_entity,
    update_user_entity,
create_user_entity_better_auth, update_user_entity_better_auth
)
from src.api.di.db_helper import db_helper
from src.config import settings
from src.schemas.webhooks import UserWebhookSchema
from src.utils.logging import logger





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
    if not verify_signature(
        raw_body, headers, settings.AUTH.CLERK_SIGNING_SECRET
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload: UserWebhookSchema = UserWebhookSchema.model_validate(raw_json)
    logger.info("[ClerkWebhook] Event %s is caught", raw_json)

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



@router.post(
    "/better-auth",
    summary="BetterAuth Webhook Handler (user.created, user.updated)",
    status_code=200,
    response_model=dict,
)
async def better_auth_webhook(
    request: Request,
    better_auth_secret: str = Header(None, alias="x-better-auth-secret"),
    db_session: AsyncSession = Depends(db_helper.session_getter),
):
    if better_auth_secret != settings.AUTH.BETTER_AUTH_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    raw_json: dict = await request.json()
    logger.debug("[BetterAuthWebhook] Raw event received: %s", raw_json)

    try:
        payload = BetterAuthWebhookSchema.model_validate(raw_json)
        logger.info("[BetterAuthWebhook] Event received: %s", payload.type)

    except ValueError as e:
        logger.error("[BetterAuthWebhook] Validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload structure",
        )

    if payload.type == "user.created":
        await create_user_entity_better_auth(payload, db_session)
        return {"message": "User created"}

    elif payload.type == "user.updated":
        await update_user_entity_better_auth(payload, db_session)
        return {"message": "User updated"}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported event type {payload.type}",
        )
