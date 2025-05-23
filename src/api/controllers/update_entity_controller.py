from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from common.functions.check_file_mime_type import is_file_mime_type_correct
from common.services.s3_service import S3Service


async def update_entity_with_optional_image(
    *,
    entity_id: UUID,
    payload: BaseModel,
    dao: Any,
    upload_path: str,
    db_session: AsyncSession,
    s3: S3Service,
    image_blob: Optional[UploadFile] = None,
) -> Any:
    data = payload.model_dump(exclude_unset=True)
    image_key: Optional[str] = None

    if image_blob:
        try:
            await is_file_mime_type_correct(image_blob)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File contents don’t match the file extension: {e}",
            )

        image_key = s3.generate_key(image_blob.filename, upload_path)
        data["image_url"] = s3.get_file_url(key=image_key)

    if not data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    try:
        updated = await dao.update(db_session, filter_by={"id": entity_id}, **data)
    except Exception as e:
        if image_key:
            await s3.remove_file(image_key)
        raise e

    if not updated:
        raise HTTPException(status_code=404, detail="Entity not found")

    if image_blob and image_key:
        await s3.upload_file(
            file=image_blob.file,
            key=image_key,
            extra_args={"ACL": "public-read", "ContentType": image_blob.content_type},
        )

    return updated
