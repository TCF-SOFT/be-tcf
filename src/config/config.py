from environs import Env
from pydantic import BaseModel
from pydantic_settings import BaseSettings

env = Env()
env.read_env()
DEV_ENV = env.bool("DEV_ENV", True)


class DatabaseConfig(BaseModel):
    PSQL_USER: str = env.str("PSQL_USER")
    PSQL_PASS: str = env.str("PSQL_PASS")
    PSQL_HOST: str = env.str("PSQL_HOST")
    PSQL_DB: str = env.str("PSQL_DB")
    TEST_PSQL_DB: str = env.str("TEST_PSQL_DB", "homebar_test")
    PSQL_URL: str = (
        f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:5432/{PSQL_DB}"
    )
    TEST_PSQL_URL: str = (
        f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:5432/{TEST_PSQL_DB}"
    )

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
    REDIS_DB: int = env.int("REDIS_DB", 5)
    INVALIDATE_CACHES_TIMEOUT: int = env.int("INVALIDATE_CACHES_TIMEOUT", 86400)
    redis_url: str = env.str("REDIS_URL")


class TelemetryConfig(BaseModel):
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

    S3_ACCESS_KEY: str = env.str("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = env.str("S3_SECRET_KEY")
    S3_BUCKET_NAME: str = env.str("S3_BUCKET_NAME", "eag-alpha2-global-models")


class SMTPConfig(BaseModel):
    """
    Represents the configuration settings for the SMTP.
    """

    smtp_host: str = env.str("SMTP_HOST", "1")
    smtp_port: int = env.int("SMTP_PORT", 1)
    smtp_user: str = env.str("SMTP_USER", "1")
    smtp_pass: str = env.str("SMTP_PASS", "1")


class Settings(BaseSettings):
    """
    Represents the configuration settings for the application.
    """

    # Application settings
    MODE: str = env.str("MODE", "DEV")

    # Database settings
    db: DatabaseConfig = DatabaseConfig()
    REDIS: RedisConfig = RedisConfig()
    TELEMETRY: TelemetryConfig = TelemetryConfig()
    AWS: AWSConfig = AWSConfig()

    # jwt_algorithm: str = env.str("JWT_ALGORITHM")
    # jwt_expire: int = env.str("JWT_EXPIRE")
    # jwt_secret: str = env.str("JWT_SECRET")
    password_manager_secret: str = env.str("PASSWORD_MANAGER_SECRET")

    # SSO
    AUTHENTIK_CLIENT_ID: str = env.str("AUTHENTIK_CLIENT_ID")
    AUTHENTIK_CLIENT_SECRET: str = env.str("AUTHENTIK_CLIENT_SECRET")

    GITHUB_CLIENT_ID: str = env.str("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = env.str("GITHUB_CLIENT_SECRET", "")
    SECRET_KEY: str = env.str("SECRET_KEY")

    # Logging settings
    PROJECT_NAME: str = env.str("PROJECT_NAME", "Home Cocktail Bar API")
    VERSION: str = env.str("VERSION", "1.0")
    DEBUG: bool = env.bool("DEBUG", False)
    SAVE_LOGS_TO_FILE: bool = env.bool("SAVE_LOGS_TO_FILE", False)
    RUN_PROD_WEB_SERVER: int = env.int("RUN_PROD_WEB_SERVER", 0) == 1
    JSON_LOG_FORMAT: bool = env.bool("JSON_LOG_FORMAT", True)

    # Telegram
    TELEGRAM_BOT_TOKEN: str = env.str("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: int = env.int("TELEGRAM_CHAT_ID")

    # Model settings
    ML_USER_MATRIX: str = env.str("ML_USER_MATRIX", "")

    # Chibisafe (CDN)
    CHIBISAFE_API_KEY: str = env.str("CHIBISAFE_API_KEY")


settings = Settings()
