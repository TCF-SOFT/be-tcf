from email.message import EmailMessage

from pydantic import EmailStr

from src.config.config import settings


def create_waybill_message(email: EmailStr) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "Прайс-лист"
    msg["From"] = settings.SMTP.SMTP_USER
    msg["To"] = email

    # TODO: add cert
    with open("src/tasks/templates/template.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Add plain text fallback
    msg.set_content(
        "Пожалуйста, ознакомьтесь с нашим коммерческим предложением. Прайс-лист во вложении."
    )

    # Add HTML content
    msg.add_alternative(html_content, subtype="html")

    return msg
