from email.message import EmailMessage

from pydantic import EmailStr

from src.config.config import settings


def create_waybill_message(email: EmailStr) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "Подтверждение о Награвании"
    msg["From"] = settings.SMTP.SMTP_USER
    msg["To"] = email
    msg.set_content(
        """
            <h1>Спасибо за награвание!</h1>
            <p>Мы обязательно свяжемся с вами в ближайшее время.</p>
        """,
        subtype="html",
    )
    return msg
