import uuid
from pathlib import Path
from typing import Any, BinaryIO

from aioboto3 import Session
from aiohttp import ClientError
from pydantic import HttpUrl

from src.config.config import settings
from utils.logging import logger


# ? Think about Singleton pattern for S3 client
class S3Service:
    """
    Wrapper around the aioboto3 S3 client.
    Methods are async.
    Compatible with FastAPI, AWS S3 and Yandex Cloud Storage.
    """

    def __init__(self):
        self._session: Session = Session(
            aws_access_key_id=settings.AWS.S3_ACCESS_KEY,
            aws_secret_access_key=settings.AWS.S3_SECRET_KEY,
            region_name=settings.AWS.S3_DEFAULT_REGION,
        )
        self._endpoint: str = settings.AWS.S3_ENDPOINT_URL
        self._bucket: str = settings.AWS.S3_BUCKET_NAME

    # ------------------------------------------------------------
    # Private factory – returns a *fresh* client every call
    # ------------------------------------------------------------
    def _client(self):
        return self._session.client("s3", endpoint_url=self._endpoint)

    # ------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------
    async def list_buckets(self) -> list[dict[str, Any]]:
        """
        List all S3 buckets.
        """
        async with self._client() as s3:
            resp = await s3.list_buckets()
            return resp.get("Buckets", [])

    async def list_objects(self, prefix: str = "") -> list[dict[str, Any]]:
        """
        List objects in a given S3 bucket with a specific prefix.
        """
        async with self._client() as s3:
            resp = await s3.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
            return resp.get("Contents", [])

    async def upload_file(
        self,
        file: BinaryIO,
        file_name: str,
        *,
        remote_path: str = "tmp/",
        bucket_name: str | None = None,
        extra_args: dict[str, Any] | None = None,
    ) -> str:
        """
        Stream `file` to S3 and return the object key.
        `remote_path` may contain slashes, is auto-trimmed, and can be blank.
        All parameters after * are keyword-only.
        """
        # ────────────────────────────────
        # 1. safe suffix extraction
        # ────────────────────────────────
        suffix = Path(file_name).suffix.lower()
        # ────────────────────────────────
        # 2. build key: <remote_path>/<uuid>.<ext>
        # ────────────────────────────────
        key = f"{remote_path.rstrip('/')}/{uuid.uuid4().hex}{suffix}".lstrip("/")
        logger.info("Uploading file to S3: %s", key)
        async with self._client() as s3:
            try:
                await s3.upload_fileobj(
                    Fileobj=file,
                    Bucket=bucket_name or self._bucket,
                    Key=key,
                    ExtraArgs=extra_args or {},
                )
            except ClientError as exc:
                logger.exception("S3 upload failed: %s", exc)
                raise

        return key

    async def remove_file(
        self,
        key: str,
        bucket_name: str | None = None,
    ) -> None:
        """
        Remove a file from S3.
        """
        async with self._client() as s3:
            try:
                await s3.delete_object(
                    Bucket=bucket_name or self._bucket,
                    Key=key,
                )
            except ClientError as exc:
                logger.exception("S3 delete failed: %s", exc)
                raise

    def get_file_url(self, key: str) -> HttpUrl | str:
        """
        Get the public URL of a file in S3.
        """
        return f"{self._endpoint}/{self._bucket}/{key}"
