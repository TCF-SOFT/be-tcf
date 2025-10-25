import importlib.metadata
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination

from src.api.di.db_helper import db_helper
from src.api.routes import router
from common.services.telemetry import setup_telemetry
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
        logger.warning("[!] Shutting down the application...")
        await app.state.redis_service.close()
        await db_helper.dispose()


if settings.SERVER.ENV == ServerEnv.PROD:
    setup_telemetry()

app = FastAPI(
    title=docs.title,
    description=docs.description,
    summary=docs.summary,
    servers=docs.servers,
    version=importlib.metadata.version(settings.PROJECT_NAME),
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
        app,
        host=settings.SERVER.HOST,
        port=settings.SERVER.PORT,
        log_config=None,
    )
