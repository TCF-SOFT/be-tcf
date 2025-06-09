from pydantic import EmailStr

from src.tasks.mailing.send_email import send_email
from pathlib import Path

template_path = Path("src/tasks/mailing/templates/pricing_email.html")

async def send_pricing_email(email: EmailStr | str) -> None:
    with open(template_path, "r", encoding="utf-8") as file:
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
        html=html
    )