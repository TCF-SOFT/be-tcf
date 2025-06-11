from pathlib import Path

from pydantic import EmailStr

from src.tasks.mailing.send_email import send_email

templates_path = Path("templates")


async def send_pricing_email(email: EmailStr | str) -> None:
    with open(templates_path / "pricing_email.html", "r", encoding="utf-8") as file:
        html = file.read()

    await send_email(
        recipient=email,
        subject="Рассылка прайсов - ТЦ Форд Севастополь",
        body="""
        Рассылка оптового прайс-листа от ford-parts.com.ru

        Скачать прайс-лист можно здесь: Прайс-лист ОПТ

        Севастополь, улица Хрусталёва, 74Ж

        РЕЖИМ РАБОТЫ
        пн‑пт 9:00‑18:00, сб 9:00‑15:00

        E‑MAIL
        fordsevas@yandex.ru
        """,
        html=html,
    )
