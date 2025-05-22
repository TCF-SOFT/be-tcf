import smtplib

from src.config.config import settings
from src.tasks.celery import celery
from src.tasks.notification import create_nagravsa_message
from src.utils.logging import logger


@celery.task
def send_nagravsa_confirmation_email(email: str):
    logger.info(f"Sending email to {email=}")
    msg_content = create_nagravsa_message(email)

    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg_content)

    return f"Email sent to {email=}"
