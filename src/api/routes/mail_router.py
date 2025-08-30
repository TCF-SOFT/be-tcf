import resend
from fastapi import APIRouter, Depends, status

from src.api.auth import validate_api_key
from src.config import settings

router = APIRouter(tags=["Mailing"], prefix="/mail")
resend.api_key = settings.SMTP.RESEND_API_KEY


@router.post(
    "/{recipient}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(validate_api_key)],
)
def send_mail(recipient) -> dict:
    params: resend.Emails.SendParams = {
        "from": "info@info.eucalytics.uk",
        "to": [f"{recipient}@gmail.com"],
        "subject": "ТЦ Форд - рассылка",
        "html": "<strong>it works!</strong> <a href=https://eucalytics.uk>Перейти на сайт</a>",
    }
    email: resend.Email = resend.Emails.send(params)
    return email
