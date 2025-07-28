import sys
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from ddtrace import patch_all
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.middleware.cors import CORSMiddleware

from api.di.db_helper import db_helper
from api.routes import router
from config.config import ServerEnv
from src.api.di.di import ResourceModule
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.common.services.redis_service import RedisService
from src.common.services.s3_service import S3Service
from src.config.config import settings
from src.docs import docs
from src.utils.logging import logger


async def check_health(app: FastAPI):
    logger.info("[!] Performing health-check of services...")
    # Check Redis health
    if not await app.state.redis.ping():
        logger.error("[X] Health-check failed: Unable to ping Redis")
        sys.exit(1)
    logger.info("[+] Redis connection established")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[!] Initializing resources...")
    app.state.resources = ResourceModule(redis_service=RedisService())
    app.state.redis_service = app.state.resources.get_redis_service()
    app.state.redis = app.state.redis_service.get_redis()
    app.state.s3 = S3Service(
        access_key=settings.AWS.S3_ACCESS_KEY,
        secret_key=settings.AWS.S3_SECRET_KEY,
        region=settings.AWS.S3_DEFAULT_REGION,
        endpoint=settings.AWS.S3_ENDPOINT_URL,
        bucket=settings.AWS.S3_BUCKET_NAME,
    )
    logger.info("[+] Resources initialized successfully")

    # Redis Cache
    FastAPICache.init(RedisBackend(app.state.redis), prefix="be-tcf")

    # Check health of services
    await check_health(app)

    try:
        yield
    finally:
        logger.info("[!] Shutting down the application...")
        await app.state.redis_service.close()
        await db_helper.dispose()  # Close the database connection pool


# Datadog tracing (should be initialized before the app creation)
if settings.TELEMETRY.DD_TRACE_ENABLED:
    patch_all(
        fastapi=True,
        loguru=True,
        redis=True,
        aiobotocore=True,
        botocore=True,
        httpx=True,
        asyncpg=True,
        openai=True,
        aiohttp=True,
    )

if settings.SERVER.ENV == ServerEnv.PROD:
    logger.info("[!] Starting the application in production mode")
    logger.info("[!] Starting sentry")
    sentry_sdk.init(
        dsn=settings.TELEMETRY.SENTRY_DSN,
        send_default_pii=True,
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        integrations=[FastApiIntegration()],
        environment=settings.SERVER.ENV,
    )

app = FastAPI(
    title=docs.title,
    description=docs.description,
    summary=docs.summary,
    servers=docs.servers,
    version="1.2.0",
    contact=docs.contact,
    openapi_url=settings.SERVER.OPENAPI_URL,
    docs_url=settings.SERVER.DOCS_URL,
    redoc_url=settings.SERVER.REDOC_URL,
    lifespan=lifespan,
)

# --------------------------------------------------
# Instrumentator (monitoring Prometheus - Grafana)
# --------------------------------------------------
# instrumentator = Instrumentator(
#     should_group_status_codes=False,
#     excluded_handlers=["/metrics"],
# )
# instrumentator.instrument(app).expose(app)

add_pagination(app)

# --------------------------------------------------
#        FastAPI Middleware (FE + Logging)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.SERVER.ALLOW_ORIGINS,
    allow_credentials=settings.SERVER.ALLOW_CREDENTIALS,
    allow_methods=settings.SERVER.ALLOW_METHODS,
    allow_headers=settings.SERVER.ALLOW_HEADERS,
)

app.middleware("http")(LoggingMiddleware())


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> ORJSONResponse:
    """
    Handles validation errors.
    Aim: handle NaN values in the request body, they can't be serialized to JSON and be returned to client.
    Library: ORJSONResponse is used to serialize NaN values to null (None).
    Source: https://github.com/tiangolo/fastapi/discussions/10141#discussioncomment-6842857
    :param _:
    :param exc:
    :return:
    """
    return ORJSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        app, host=settings.SERVER.HOST, port=settings.SERVER.PORT, log_config=None
    )
