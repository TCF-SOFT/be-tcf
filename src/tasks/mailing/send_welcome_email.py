from schemas.user_schema import UserRead
from src.tasks.mailing.send_email import send_email


async def send_welcome_email(user: UserRead) -> None:
    await send_email(
        recipient=str(user.email),
        subject="Welcome to our site!",
        body=f"Dear {user.first_name},\n\nWelcome to our site!",
    )