import sys
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from app.api.admin.auth import authentication_backend_admin
from app.api.admin.auth import authentik
from app.api.admin.auth import get_current_user
from app.api.admin.views import CocktailAdmin
from app.api.admin.views import ImageAdmin
from app.api.admin.views import LabelAdmin
from app.api.admin.views import OrderAdmin
from app.api.admin.views import OrderCocktailAdmin
from app.api.admin.views import RatingAdmin
from app.api.admin.views import UserAdmin
from app.api.di.database import engine
from app.api.di.di import get_redis
from app.api.middleware.logging_middleware import LoggingMiddleware
from app.api.routes.auth_router import router as auth_router
from app.api.routes.cart_router import router as cart_router
from app.api.routes.file_router import router as file_router
from app.api.routes.image_router import router as image_router
from app.api.routes.label_router import router as label_router
from app.api.routes.order_router import router as order_router
from app.api.routes.product_router import router as product_router
from app.api.routes.rating_router import router as rating_router
from app.api.routes.user_router import router as user_router
from app.api.routes.utils_router import router as utils_router
from app.config.config import settings
from app.utils.logging import logger

# from ddtrace import patch, config


async def check_health(app: FastAPI):
    logger.info("[!] Performing health-check of services...")
    # Check Redis health
    if reddis_check := await app.state.redis.ping():
        logger.info(f"[+] Redis connection established: {reddis_check=}")
    else:
        logger.error("[X] Redis connection failed")
        sys.exit(1)


# --------------------------------------------------
#  FastAPI Services Lifespan (Startup and Shutdown)
#  - logger
#  - redis caching
#  - health-check
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the redis connection
    app.state.redis = await get_redis()

    # Check health of services
    await check_health(app)
    logger.info("[+] Health-check of services was successful")

    # FastAPI Cache (https://github.com/long2ice/fastapi-cache)
    FastAPICache.init(RedisBackend(app.state.redis), prefix="be-home-bar")

    # Sentry
    if settings.RUN_PROD_WEB_SERVER:
        logger.info("[!] Starting the application in production mode")
        logger.info("[!] Starting sentry")
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            # TODO: utils, Get microserver version
            release=settings.VERSION,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

        # Datadog
        # logger.info("[!] Starting Datadog")
        # patch(sqlalchemy=True)
        # patch(redis=True)
        # patch(fastapi=True)
        # patch(psygopg=True)
        # config.service = "be-home-bar"

    try:
        yield
    finally:
        # close redis connection and release the resources

        await app.state.redis.close()
        logger.info("[!] Shutting down the application...")


app = FastAPI(
    title="Home Cocktail Bar",
    version="1.0.0",
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
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

# --------------------------------------------------
#            FastAPI Middleware (FE)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://api-bar.eucalytics.uk",
        "https://bar.eucalytics.uk",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Authorization",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
    ],
)

app.middleware("http")(LoggingMiddleware())

# Cookie-based session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
)
# --------------------------------------------------
#               FastAPI Routers
# --------------------------------------------------
app.include_router(user_router)
app.include_router(product_router)
app.include_router(label_router)
app.include_router(auth_router)
app.include_router(image_router)
app.include_router(utils_router)
app.include_router(order_router)
app.include_router(cart_router)
app.include_router(rating_router)
app.include_router(file_router)

# should be after the routers (https://stackoverflow.com/a/76894187)
add_pagination(app)

# --------------------------------------------------
#               FastAPI Admin Panel
# --------------------------------------------------
admin = Admin(app, engine, authentication_backend=authentication_backend_admin)
# admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(CocktailAdmin)
admin.add_view(ImageAdmin)
admin.add_view(OrderAdmin)
admin.add_view(OrderCocktailAdmin)
admin.add_view(LabelAdmin)
admin.add_view(RatingAdmin)


# Защита документации с помощью зависимости Depends
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(user: dict = Depends(get_current_user)):
    # Поскольку Depends вызовет get_current_user, если пользователь не авторизован, он выбросит исключение
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False)
async def custom_swagger_ui_redoc(user: dict = Depends(get_current_user)):
    # Поскольку Depends вызовет get_current_user, если пользователь не авторизован, он выбросит исключение
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_user)):
    return get_openapi(title="FastAPI", version=app.version, routes=app.routes)


async def login_authentik(request: Request) -> Response:
    token = await authentik.authorize_access_token(request)
    user = token.get("id_token")
    print(f"Admin: {user}")

    if user:
        request.session["user"] = user
    return RedirectResponse(request.url_for("admin:index"))


admin.app.add_route("/auth/authentik", login_authentik)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config=None,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
