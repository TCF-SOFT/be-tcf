from fastapi import APIRouter
from pydantic import EmailStr

from src.tasks.tasks import send_waybill_confirmation_email

router = APIRouter(tags=["Waybill"])


@router.get("/waybill/{email}", status_code=200)
async def send_waybill(email: EmailStr) -> None:
    """
    Send waybill to email
    """
    send_waybill_confirmation_email.delay(email=email)
