from email.message import EmailMessage

import aiosmtplib
from pydantic import EmailStr

from src.config import settings
from src.utils.logging import logger


async def send_email(
    recipient: EmailStr | str,
    subject: str,
    body: str,
    html: str | None = None,
):
    recipient = str(recipient)
    admin_email = settings.SMTP.SMTP_USER

    message = EmailMessage()
    message["From"] = admin_email
    message["To"] = recipient
    message["Subject"] = subject

    # Plain text (fallback)
    message.set_content(body)

    if html:  # HTML Rendered override
        message.add_alternative(html, subtype="html")

    await aiosmtplib.send(
        message,
        sender=admin_email,
        recipients=[recipient],
        hostname=settings.SMTP.SMTP_HOST,
        port=settings.SMTP.SMTP_PORT,
        username=settings.SMTP.SMTP_USER,
        password=settings.SMTP.SMTP_PASS,
        start_tls=True,
    )
    logger.info("Email was sent to %r", recipient)
