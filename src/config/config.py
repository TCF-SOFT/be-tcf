from environs import Env
from pydantic import BaseModel
from pydantic_settings import BaseSettings

env = Env()
env.read_env()
DEV_ENV = env.bool("DEV_ENV", True)


class DatabaseConfig(BaseModel):
    """
    Represents the configuration settings for the database.
    """

    PSQL_USER: str = env.str("PSQL_USER")
    PSQL_PASS: str = env.str("PSQL_PASS")
    PSQL_HOST: str = env.str("PSQL_HOST")
    PSQL_DB: str = env.str("PSQL_DB")
    PSQL_PORT: int = env.int("PSQL_PORT", 5432)
    TEST_PSQL_DB: str = env.str("TEST_PSQL_DB", "tcf_test")

    PSQL_URL: str = f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"
    TEST_PSQL_URL: str = f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:{PSQL_PORT}/{TEST_PSQL_DB}"

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


class ElasticSearchConfig(BaseModel):
    """
    Represents the configuration settings for the ElasticSearch.
    """

    # ELASTIC_HOST: str = env.str("ELASTIC_HOST")
    # ELASTIC_PORT: int = env.int("ELASTIC_PORT", 9200)
    # ELASTIC_USER: str = env.str("ELASTIC_USER")
    # ELASTIC_API_KEY: str = env.str("ELASTIC_API_KEY")
    # ELASTIC_INDEX: str = env.str("ELASTIC_INDEX", "stat_agg")
    pass


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

    S3_ACCESS_KEY: str = env.str("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = env.str("S3_SECRET_KEY")
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
    pass


class SecurityConfig(BaseModel):
    """
    Represents the configuration settings for the security.
    """

    # JWT_ALGORITHM: str = env.str("JWT_ALGORITHM")
    # JWT_EXPIRE: int = env.str("JWT_EXPIRE")
    # JWT_SECRET: str = env.str("JWT_SECRET")
    # PASSWORD_MANAGER_SECRET: str = env.str("PASSWORD_MANAGER_SECRET")
    #
    # AUTHENTIK_CLIENT_ID: str = env.str("AUTHENTIK_CLIENT_ID")
    # AUTHENTIK_CLIENT_SECRET: str = env.str("AUTHENTIK_CLIENT_SECRET")
    pass


class Settings(BaseSettings):
    """
    Represents the configuration settings for the application.
    """

    # Application settings
    MODE: str = env.str("MODE", "DEV")

    # Database settings
    ES: ElasticSearchConfig = ElasticSearchConfig()
    DB: DatabaseConfig = DatabaseConfig()
    REDIS: RedisConfig = RedisConfig()
    TELEMETRY: TelemetryConfig = TelemetryConfig()
    AWS: AWSConfig = AWSConfig()
    SMTP: SMTPConfig = SMTPConfig()
    SECURITY: SecurityConfig = SecurityConfig()

    # Logging settings
    PROJECT_NAME: str = env.str("PROJECT_NAME", "be-tcf")
    DEBUG: bool = env.bool("DEBUG", False)
    SAVE_LOGS_TO_FILE: bool = env.bool("SAVE_LOGS_TO_FILE", False)
    RUN_PROD_WEB_SERVER: int = env.int("RUN_PROD_WEB_SERVER", 0)
    JSON_LOG_FORMAT: bool = env.bool("JSON_LOG_FORMAT", True)

    # OpenAI
    OPENAI_API_KEY: str = env.str("OPENAI_API_KEY")


settings = Settings()
