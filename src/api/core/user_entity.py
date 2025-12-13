from sqlalchemy.ext.asyncio import AsyncSession

from schemas.webhooks import BetterAuthWebhookSchema
from src.api.dao.user_dao import UserDAO
from src.schemas.common.enums import CustomerType, Role
from src.schemas.user_schema import UserCreate
from src.utils.logging import logger

# --------------------------------- Disclaimer ----------------------------------#
# This is custom not generic create/update functions because of BetterAuth Webhook
# These functions handles custom logic of user creation after Sign-up process & Profile update
# --------------------------------------------------------------------------------#


async def create_user_entity(
    payload: BetterAuthWebhookSchema,
    db_session: AsyncSession,
):
    data = payload.data

    user = UserCreate(
        id=data.id,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        is_active=True,
        role=Role.USER,
        customer_type=CustomerType.USER_RETAIL,
        mailing=False,
        phone=None,
        city=None,
        note=None,
        shipping_method=None,
        shipping_company=None,
        balance_rub=0,
        balance_usd=0,
        balance_eur=0,
        balance_try=0,
    )

    logger.info("[Webhook] Creating user %s", user.email)
    try:
        await UserDAO.add(db_session, **user.model_dump())
        logger.info("[Webhook] User %s is created", user.email)
    except Exception as e:
        logger.error("[Webhook] Error creating user %s: %s", user.email, str(e))


async def update_user_entity(
    payload: BetterAuthWebhookSchema,
    db_session: AsyncSession,
):
    data = payload.data
    logger.info(
        "[Webhook] Updating user ID %s",
        data.id,
    )
    try:
        await UserDAO.update(
            db_session,
            {"id": data.id},
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    except Exception as e:
        logger.error("[Webhook] Error updating user ID %s: %s", data.id, str(e))


async def delete_user_entity(
    payload: BetterAuthWebhookSchema,
    db_session: AsyncSession,
):
    user_data = payload.data
    logger.info(
        "[DELETE] Deleting user: %s",
        user_data.id,
    )
    return await UserDAO.delete_by_id(db_session, user_data.id)
