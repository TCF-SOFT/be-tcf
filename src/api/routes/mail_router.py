import resend
from fastapi import APIRouter, status

from config import settings

router = APIRouter(tags=["Mailing"], prefix="/mail")
resend.api_key = settings.SMTP.RESEND_API_KEY

f: bytes = open("price_opt.xlsx", "rb").read()
attachment: resend.Attachment = {"content": list(f), "filename": "price_opt.xlsx"}


@router.post(
    "",
    status_code=status.HTTP_200_OK,
)
def send_mail() -> dict:
    params: resend.Emails.SendParams = {
        "from": "info@info.eucalytics.uk",
        "to": ["utikpuhlik@gmail.com"],
        "subject": "ТЦ Форд - рассылка",
        "html": "<strong>it works!</strong> <a href=https://eucalytics.uk>Перейти на сайт</a>",
        "attachments": [attachment],
    }
    email: resend.Email = resend.Emails.send(params)
    return email
