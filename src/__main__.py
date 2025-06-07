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
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.middleware.cors import CORSMiddleware

from common.services.s3_service import S3Service
from src.api.controllers.api_microservice_version import get_microservice_version
from src.api.di.di import ResourceModule
from src.api.di.redis_service import RedisService
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.api.routes.category_router import router as category_router
from src.api.routes.health_check_router import router as health_check_router
from src.api.routes.offer_router import router as offer_router
from src.api.routes.pricing_router import router as pricing_router
from src.api.routes.product_router import router as product_router
from src.api.routes.sub_category_router import router as sub_category_router
from src.api.routes.user_router import router as user_router
from src.api.routes.version_router import router as version_router
from src.api.routes.waybill_router import router as waybill_router
from src.config.config import settings
from src.docs import docs
from src.utils.logging import logger


async def check_health(app: FastAPI):
    logger.info("[!] Performing health-check of services...")
    # Check Redis health
    if not await app.state.resources.get_redis().ping():
        logger.error("[X] Health-check failed: Unable to ping Redis")
        sys.exit(1)
    logger.info("[+] Redis connection established")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.RUN_PROD_WEB_SERVER:
        logger.info("[!] Starting the application in production mode")
        logger.info("[!] Starting sentry")
        sentry_sdk.init(
            dsn=settings.TELEMETRY.SENTRY_DSN,
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            send_default_pii=True,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for tracing.
            traces_sample_rate=1.0,
            # Set profile_session_sample_rate to 1.0 to profile 100%
            # of profile sessions.
            profile_session_sample_rate=1.0,
            # Set profile_lifecycle to "trace" to automatically
            # run the profiler on when there is an active transaction
            profile_lifecycle="trace",
            integrations=[FastApiIntegration()],
            release=await get_microservice_version(),
            environment=settings.MODE,
        )

    # Resources initialization
    logger.info("[!] Initializing resources...")
    app.state.resources = ResourceModule(redis=RedisService())
    app.state.s3 = S3Service()
    logger.info("[+] Resources initialized successfully")

    # Redis Cache
    FastAPICache.init(RedisBackend(app.state.resources.get_redis()), prefix="be-tcf")

    # Check health of services
    await check_health(app)

    try:
        yield
    finally:
        logger.info("[!] Shutting down the application...")


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

app = FastAPI(
    title=docs.title,
    description=docs.description,
    summary=docs.summary,
    servers=docs.servers,
    version="1.2.0",
    contact=docs.contact,
    openapi_url="/docs/pricing-v2/openapi.json",
    # docs_url=docs.DOCS_URL,
    # redoc_url=docs.REDOC_URL,
    lifespan=lifespan,
)

# --------------------------------------------------
# Instrumentator (monitoring Prometheus - Grafana)
# --------------------------------------------------
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
)
instrumentator.instrument(app).expose(app)

add_pagination(app)

# --------------------------------------------------
#            FastAPI Middleware (FE)
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


app.include_router(category_router)
app.include_router(sub_category_router)
app.include_router(product_router)
app.include_router(offer_router)
app.include_router(user_router)
app.include_router(waybill_router)
app.include_router(pricing_router)
app.include_router(health_check_router)
app.include_router(version_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=None)
