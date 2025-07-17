from enum import Enum

from environs import Env
from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic_settings import BaseSettings

env = Env()

# Decide which .env file to use based on the PYTHON_ENV environment variable
env_file = ".env.test" if env.str("PYTHON_ENV", "dev") == "test" else ".env"
env.read_env(env_file)


class ServerEnv(str, Enum):
    TEST = "TEST"
    DEV = "DEV"
    PROD = "PROD"


class DatabaseConfig(BaseModel):
    """
    Represents the configuration settings for the database.
    """

    PSQL_USER: str = env.str("PSQL_USER")
    PSQL_PASS: str = env.str("PSQL_PASS")
    PSQL_HOST: str = env.str("PSQL_HOST")
    PSQL_DB: str = env.str("PSQL_DB")
    PSQL_PORT: int = 5432

    PSQL_URL: PostgresDsn = f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RedisConfig(BaseModel):
    """
    Represents the configuration settings for the Redis database.
    """

    REDIS_HOST: str = env.str("REDIS_HOST")
    REDIS_PORT: int = env.int("REDIS_PORT", 6379)
    REDIS_DB: int = env.int("REDIS_DB", 0)
    INVALIDATE_CACHES_TIMEOUT: int = env.int("INVALIDATE_CACHES_TIMEOUT", 86400)


class TelemetryConfig(BaseModel):
    """
    Represents the configuration settings for the telemetry.
    """

    SENTRY_DSN: str = env.str("SENTRY_DSN", "")
    DD_TRACE_ENABLED: bool = env.str("DD_TRACE_ENABLED", "False").lower() in (
        "true",
        "1",
        "t",
    )


class AWSConfig(BaseModel):
    """
    Represents the configuration settings for the AWS Resources.
    """

    S3_ACCESS_KEY: str = env.str("S3_ACCESS_KEY", "test")
    S3_SECRET_KEY: str = env.str("S3_SECRET_KEY", "test")
    S3_DEFAULT_REGION: str = env.str("S3_DEFAULT_REGION", "storage")

    S3_BUCKET_NAME: str = env.str("S3_BUCKET_NAME", "tcf-images")
    S3_ENDPOINT_URL: str = env.str("S3_ENDPOINT_URL", "https://storage.yandexcloud.net")


class SMTPConfig(BaseModel):
    """
    Represents the configuration settings for the SMTP.
    """

    SMTP_HOST: str = env.str("SMTP_HOST")
    SMTP_PORT: int = env.int("SMTP_PORT")
    SMTP_USER: str = env.str("SMTP_USER")
    SMTP_PASS: str = env.str("SMTP_PASS")


class AuthConfig(BaseModel):
    CLERK_SECRET_KEY: str = env.str("CLERK_SECRET_KEY")
    AUTHORIZED_PARTIES: list[str] = ["http://localhost:3000, https://tcf.eucalytics.uk"]

    # AUTHENTIK_CLIENT_ID: str = env.str("AUTHENTIK_CLIENT_ID")
    # AUTHENTIK_CLIENT_SECRET: str = env.str("AUTHENTIK_CLIENT_SECRET")


class ServerConfig(BaseModel):
    """
    Represents the configuration settings for the server.
    """

    HOST: str = "0.0.0.0"
    PORT: int = 8080
    ENV: ServerEnv = env.str("ENV", "DEV").upper()

    # CORS settings
    ALLOW_ORIGINS: list[str] = [
        "https://tcf.eucalytics.uk",
        "http://localhost:3000",
    ]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOW_HEADERS: list[str] = [
        "Content-Type",
        "Set-Cookie",
        "Authorization",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
    ]

    @computed_field
    def DOCS_URL(self) -> str | None:
        return "/docs" if self.ENV in (ServerEnv.DEV, ServerEnv.TEST) else None

    @computed_field
    def REDOC_URL(self) -> str | None:
        return "/redoc" if self.ENV in (ServerEnv.DEV, ServerEnv.TEST) else None

    @computed_field
    def OPENAPI_URL(self) -> str | None:
        return (
            "/docs/openapi.json"
            if self.ENV in (ServerEnv.DEV, ServerEnv.TEST)
            else None
        )


class Settings(BaseSettings):
    """
    Represents the configuration settings for the application.
    """

    # Application settings
    MODE: str = env.str("MODE", "DEV")
    RUN_PROD_WEB_SERVER: int = env.int("RUN_PROD_WEB_SERVER", 0)

    DB: DatabaseConfig = DatabaseConfig()
    REDIS: RedisConfig = RedisConfig()

    TELEMETRY: TelemetryConfig = TelemetryConfig()
    AWS: AWSConfig = AWSConfig()
    SMTP: SMTPConfig = SMTPConfig()
    AUTH: AuthConfig = AuthConfig()

    SERVER: ServerConfig = ServerConfig()

    # Logging settings
    JSON_LOG_FORMAT: bool = env.bool("JSON_LOG_FORMAT", True)
    DEBUG: bool = env.bool("DEBUG", False)
    SAVE_LOGS_TO_FILE: bool = env.bool("SAVE_LOGS_TO_FILE", False)
    PROJECT_NAME: str = env.str("PROJECT_NAME", "be-tcf")

    # OpenAI (Not used yet)
    OPENAI_API_KEY: str = env.str("OPENAI_API_KEY", "")
    IMAGE_PLACEHOLDER_URL: str = (
        "https://storage.yandexcloud.net/tcf-images/default.svg"
    )


settings = Settings()
