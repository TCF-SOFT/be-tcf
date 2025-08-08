import sentry_sdk
from ddtrace import patch_all
from sentry_sdk.integrations.fastapi import FastApiIntegration

from config import settings
from utils.logging import logger


def setup_telemetry():
    """
    Initializes telemetry services for the application.
    - Sentry for error tracking
    - Datadog for distributed tracing and performance monitoring
    """
    logger.warning("[!] Starting the application in production mode")
    if settings.TELEMETRY.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.TELEMETRY.SENTRY_DSN,
            send_default_pii=True,
            traces_sample_rate=1.0,
            profile_session_sample_rate=1.0,
            profile_lifecycle="trace",
            integrations=[FastApiIntegration()],
            environment=settings.SERVER.ENV,
        )
        logger.info("[Telemetry] Sentry initialized successfully")
    else:
        logger.warning(
            "[Telemetry] Sentry initialization skipped, SENTRY_DSN is not set"
        )
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
        logger.info("[Telemetry] Datadog tracing initialized successfully")
    else:
        logger.warning(
            "[Telemetry] Datadog tracing is disabled, DD_TRACE_ENABLED is not set to True"
        )
