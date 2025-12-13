from datetime import datetime

import resend
from fastapi import APIRouter, Depends, status
from jinja2 import Environment, FileSystemLoader

from src.api.auth import validate_api_key
from src.config import settings

router = APIRouter(tags=["Mailing"], prefix="/mail")
resend.api_key = settings.SMTP.RESEND_API_KEY


env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("pricing_email.html")

now = datetime.now()
html = template.render(
    pricelist_url=f"{settings.AWS.S3_ENDPOINT_URL}/tcf-images/tmp/price_list_{now.strftime('%d_%m_%Y')}.xlsx"
)


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
        "html": html,
    }
    email: resend.Email = resend.Emails.send(params)
    return email
