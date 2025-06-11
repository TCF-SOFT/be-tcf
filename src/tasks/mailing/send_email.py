from email.message import EmailMessage

import aiosmtplib
from pydantic import EmailStr

from src.config.config import settings
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
        hostname=settings.SMTP.SMTP_HOST
        if settings.RUN_PROD_WEB_SERVER
        else "localhost",
        port=settings.SMTP.SMTP_PORT if settings.RUN_PROD_WEB_SERVER else 1025,
        username=settings.SMTP.SMTP_USER if settings.RUN_PROD_WEB_SERVER else None,
        password=settings.SMTP.SMTP_PASS if settings.RUN_PROD_WEB_SERVER else None,
        start_tls=True if settings.RUN_PROD_WEB_SERVER else None,
    )
    logger.warning("Email was sent to %r", recipient)
