from clerk_backend_api import Clerk
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.user_dao import UserDAO
from src.schemas.common.enums import CustomerType, Role
from src.schemas.user_schema import UserCreate
from src.schemas.webhooks.clerk_webhook_schema import UserWebhookSchema
from src.schemas.webhooks.common import UserWebhookData
from src.utils.logging import logger

# ------------------------------ Disclaimer ------------------------------#
# This is custom not generic create/update functions because of Clerk Webhook
# These functions handles custom logic of user creation after Sign-up process


async def create_user_entity(
    payload: UserWebhookSchema,
    db_session: AsyncSession,
    clerk_client: Clerk,
) -> None:
    """
    Create a new user entity in the database
    Flow:
    1. Extract user data from the payload
    2. Validate with UserCreate pydantic schema
    3. Create a User instance with **kwargs
    """

    user_data: UserWebhookData = payload.data

    user_create = UserCreate(
        clerk_id=user_data.clerk_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True,
        role=Role.USER,
        customer_type=CustomerType.USER_RETAIL,
        mailing=False,
        phone=None,
        city=None,
        note=None,
        shipping_method=None,
        shipping_company=None,
    )
    logger.info(
        "[ClerkWebhook | POST] Creating user %s",
        user_data.email_addresses[0].email_address,
    )
    internal_user = await UserDAO.add(db_session, **user_create.model_dump())
    logger.info(
        "[ClerkWebhook | POST] User %s is created",
        user_data.email_addresses[0].email_address,
    )

    await clerk_client.users.update_metadata_async(
        user_id=payload.data.clerk_id,
        public_metadata={
            "_id": internal_user.id,
            "_role": internal_user.role,
            "_customer_type": internal_user.customer_type,
        },
    )
    logger.info("[ClerkWebhook | POST] User metadata updated in Clerk")


async def update_user_entity(
    payload: UserWebhookSchema,
    db_session: AsyncSession,
) -> None:
    """
    Update a user entity in the database
    """
    user_data = payload.data
    logger.info(
        "[ClerkWebhook | PATCH] Updating user: %s",
        user_data.clerk_id,
    )
    return await UserDAO.update(
        db_session,
        {"clerk_id": user_data.clerk_id},
        **user_data.model_dump(
            exclude={
                "primary_email_address_id",
                "primary_phone_number_id",
                "email_addresses",
                "phone_numbers",
            }
        ),
    )


async def delete_user_entity(
    payload: UserWebhookSchema,
    db_session: AsyncSession,
):
    user_data = payload.data
    logger.info(
        "[ClerkWebhook | DELETE] Deleting user: %s",
        user_data.clerk_id,
    )
    return await UserDAO.delete_by_clerk_id(db_session, user_data.clerk_id)
