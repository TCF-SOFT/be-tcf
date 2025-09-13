from datetime import datetime
from typing import BinaryIO

from fastapi import APIRouter, Depends, status
from pydantic import HttpUrl

from src.api.auth import validate_api_key
from src.api.core.price_service import fetch_price_list
from src.common.deps.s3_service import get_s3_service
from src.common.services.s3_service import S3Service

router = APIRouter(tags=["Documents"], prefix="/documents")


@router.post(
    "/price",
    summary="Upload PriceList to S3 and return a presigned URL",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(validate_api_key)],
)
async def upload_price_and_get_link(
    s3: S3Service = Depends(get_s3_service),
) -> dict[str, HttpUrl | str]:
    now = datetime.now()
    key = s3.generate_key(
        f"price_list_{now.strftime('%d_%m_%Y')}.xlsx", use_file_name=True
    )
    url = s3.get_file_url(key)

    price_file: BinaryIO = await fetch_price_list()

    await s3.upload_file(
        file=price_file,
        key=key,
        extra_args={
            "ACL": "public-read",
            "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
    )
    return {"url": url}
