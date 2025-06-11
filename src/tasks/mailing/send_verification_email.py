from src.models import User
from src.tasks.mailing.send_email import send_email


async def send_verification_email(user: User) -> None:
    await send_email(
        recipient=user.email,
        subject="Please confirm you registration!",
        body=f"Dear {user.first_name},\n\nPlease confirm you registration!",
    )
