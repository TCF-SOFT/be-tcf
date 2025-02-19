import io
from pathlib import Path
from typing import Union

import pandas as pd
from boto3 import Session
from redis.asyncio import ConnectionPool, Redis
from sklearn.metrics.pairwise import cosine_similarity

from src.config.config import DEV_ENV, settings
from src.config.config import settings as global_settings
from src.utils.logging import logger
from src.utils.singleton import SingletonMeta

if DEV_ENV:
    # Local development
    # FROM_URL = redis://, rediss://, unix://
    # DEFAULT with https
    redis_host = global_settings.redis_url
else:
    redis_host = "redis"


def redis_connection_pool() -> ConnectionPool:
    return ConnectionPool(host=redis_host, port=6379, db=0)


pool = redis_connection_pool()


async def get_redis() -> Redis:
    return Redis(
        connection_pool=pool, ssl=True, encoding="utf-8", decode_responses=True
    )


class S3Service(metaclass=SingletonMeta):
    __session: Session = None
    _s3: Session.client = None
    _folder: Path = None

    def __init__(self):
        self.__session: Session = self._create_session()
        self._s3: Session.client = self._create_s3_client()
        self._folder: Path = Path("tmp/")
        if not self._folder.exists():
            self._folder.mkdir()

    @staticmethod
    def _create_session() -> Session:
        session = Session(
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        return session

    def _create_s3_client(self) -> Session.client:
        return self.__session.client("s3")

    def get_s3_client(self) -> Session.client:
        return self._s3

    def list_buckets(self) -> dict:
        buckets = self._s3.list_buckets()
        return buckets["Buckets"]

    def list_objects(self, bucket_name: str = settings.S3_BUCKET_NAME) -> dict:
        objects = self._s3.list_objects(Bucket=bucket_name)
        return objects["Contents"]

    def io_download(
        self, path: str, bucket_name: str = settings.S3_BUCKET_NAME
    ) -> io.BytesIO or None:
        """
        Download file from S3 to memory
        :param bucket_name:
        :param path: the path to the file in S3 in the format 'folder/file.format'
        :return:
        """
        try:
            logger.info(f"Downloading from S3: {path}")
            response = self._s3.get_object(Bucket=bucket_name, Key=path)
            return response["Body"]
        except Exception as e:
            logger.error(f"Error downloading from S3: {e}")
            return None

    def local_download(
        self,
        path: str,
        name: Union[str, Path],
        bucket_name: str = settings.S3_BUCKET_NAME,
        folder=None,
        verbose=True,
        force=False,
    ) -> None:
        """
        Download file from S3 to local
        :param name:  file name, automatically download to /tmp folder
        :param folder:  local folder to save file [optional]
        :param bucket_name: [optional]
        :param path: the path to the file in S3 in the format 'folder/file.format'
        :param verbose: [optional]
        :param force: [optional] force download even if the file exists
        :return:
        """
        # Check if the file already exists
        if (self._folder / name).exists() and not force:
            return

        try:
            target_folder = folder if folder else self._folder
            target_path = target_folder / name

            if verbose:
                logger.info(f"Downloading from S3: {path} to {target_path}..")

            self._s3.download_file(bucket_name, path, target_path)
        except Exception as e:
            logger.debug(f"Error downloading from S3 to local: {e}")


def get_s3_service() -> S3Service:
    """
    Dependency to get the S3 service
    """
    return S3Service()


class URM(metaclass=SingletonMeta):
    """
    URM: User Recommendation Matrix
    """

    s3_service: S3Service = get_s3_service()
    user_item_matrix: pd.DataFrame = None
    folder: Path = Path("tmp/")

    def __init__(self):
        self.user_item_matrix: pd.DataFrame = self.prepare_user_item_matrix()

    def prepare_user_item_matrix(self) -> pd.DataFrame:
        """
        Prepare the user-item matrix
        """
        if not self.user_item_matrix:
            self.s3_service.local_download(
                settings.ML_USER_MATRIX, "cocktail_tables.csv"
            )
            logger.info("Initializing the user-item matrix...")
            self.user_item_matrix = pd.read_csv(
                self.folder / "cocktail_tables.csv"
            ).set_index("Name")
            self.user_item_matrix.drop(columns=["Main", "Tags", "Eval"], inplace=True)
        return self.user_item_matrix

    def calculate_user_similarity(self) -> pd.DataFrame:
        """
        Calculate the cosine similarity between users
        """
        user_item_matrix_filled = self.user_item_matrix.fillna(0)
        user_similarity = cosine_similarity(user_item_matrix_filled.T)
        user_similarity_df = pd.DataFrame(
            user_similarity,
            index=user_item_matrix_filled.columns,
            columns=user_item_matrix_filled.columns,
        )
        return user_similarity_df
