from typing import Annotated, Any, Sequence

from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions.exceptions import DuplicateNameError
from common.functions.check_file_mime_type import is_file_mime_type_correct
from common.services.s3_service import S3Service
from utils.logging import logger


async def create_entity_with_image(
    *,
    payload: BaseModel,
    image_blob: UploadFile,
    dao: Any,
    upload_path: str,
    db_session: AsyncSession,
    s3: S3Service,
    refresh_fields: Sequence[str] = (),
    exception_cls: type[Exception] = DuplicateNameError,
) -> Annotated[Any | None, "SQLAlchemy Instance"]:
    try:
        await is_file_mime_type_correct(image_blob)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File contents don’t match the file extension: {e}",
        )

    image_key = s3.generate_key(image_blob.filename, upload_path)
    payload.image_url = s3.get_file_url(key=image_key)

    try:
        instance = await dao.add(**payload.model_dump(), db_session=db_session)

        if refresh_fields:
            await db_session.refresh(instance, list(refresh_fields))

        await s3.upload_file(
            file=image_blob.file,
            key=image_key,
            extra_args={"ACL": "public-read", "ContentType": image_blob.content_type},
        )
        return instance
    except exception_cls as e:
        logger.warning(f"Duplicate name/slug: {getattr(payload, 'slug', 'unknown')}")
        raise e
