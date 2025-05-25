import smtplib
from email.message import EmailMessage

from pydantic import EmailStr

from src.config.config import settings
from src.tasks.celery import celery
from src.tasks.notification import create_waybill_message
from src.utils.logging import logger


@celery.task
def send_waybill_confirmation_email(email: EmailStr):
    logger.info(f"Sending email to {email=}")
    msg_content: EmailMessage = create_waybill_message(email)

    with smtplib.SMTP(settings.SMTP.SMTP_HOST, settings.SMTP.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP.SMTP_USER, settings.SMTP.SMTP_PASS)
        server.send_message(msg_content)

    return f"Email sent to {email=}"
