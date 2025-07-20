from sqlalchemy.ext.asyncio import AsyncSession

from schemas.common.enums import CustomerType, Role, ShippingMethod
from src.api.dao.user_dao import UserDAO
from src.schemas.clerk_webhook_schema import ClerkWebhookSchema
from src.schemas.user_schema import UserCreate
from utils.logging import logger

# ------------------------------ Disclaimer ------------------------------#
# This is custom not generic create/update functions because of Clerk Webhook
# These functions handles custom logic of user creation after Sign-up processs


async def create_user_entity(
    payload: ClerkWebhookSchema,
    db_session: AsyncSession,
) -> None:
    """
    Create a new user entity in the database
    Flow:
    1. Extract user data from the payload
    2. Validate with UserCreate pydantic schema
    3. Create a User instance with **kwargs
    """

    user_data = payload.data

    user_create = UserCreate(
        clerk_id=user_data.id,
        email=user_data.email_addresses[0].email_address,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=~user_data.banned,
        role=Role.USER,
        customer_type=CustomerType.USER_RETAIL,
        mailing=False,
        phone=None,
        city=None,
        notes=None,
        shipping_method=ShippingMethod.OTHER,
        shipping_company=None,
    )
    logger.info(
        "[Webhook | POST] Creating user %s", user_data.email_addresses[0].email_address
    )
    await UserDAO.add(db_session, **user_create.model_dump())
    logger.info(
        "[Webhook | POST] User %s is created",
        user_data.email_addresses[0].email_address,
    )


async def update_user_entity(
    payload: ClerkWebhookSchema,
    db_session: AsyncSession,
) -> None:
    """
    Update a user entity in the database
    """
    user_data = payload.data
    logger.info(
        "[Webhook | PATCH] Updating user %s with id: %s",
        user_data.email_addresses[0].email_address,
        user_data.id,
    )


async def delete_user_entity(
    payload: ClerkWebhookSchema,
    db_session: AsyncSession,
):
    user_data = payload.data
    clerk_id = user_data.id
    return await UserDAO.delete_by_clerk_id(db_session, clerk_id)
