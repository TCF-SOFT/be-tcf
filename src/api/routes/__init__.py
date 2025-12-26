from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.routes.integrations.documents_router import router as documents_router
from api.routes.integrations.integration_router import router as integration_router
from api.routes.integrations.mail_router import router as mail_router
from api.routes.integrations.webhook_router import router as webhook_router
from api.routes.utils.health_check_router import router as health_check_router
from api.routes.utils.version_router import router as version_router

from .analytical_router import router as analytical_router
from .audit_log_router import router as audit_log_router
from .category_router import router as category_router
from .offer_router import router as offer_router
from .order_offers_router import router as order_offers_router
from .order_router import router as order_router
from .product_router import router as product_router
from .sub_category_router import router as sub_category_router
from .user_balance_router import router as user_balance_history_router
from .user_router import router as user_router
from .waybill_offers_router import router as waybill_offers_router
from .waybill_router import router as waybill_router

# TODO: add v1 prefix

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(dependencies=[Depends(http_bearer)])

# Include all routers
router.include_router(user_router)
router.include_router(user_balance_history_router)
router.include_router(category_router)
router.include_router(sub_category_router)
router.include_router(product_router)
router.include_router(offer_router)
router.include_router(waybill_router)
router.include_router(waybill_offers_router)
router.include_router(order_router)
router.include_router(order_offers_router)
router.include_router(analytical_router)
router.include_router(webhook_router)
router.include_router(health_check_router)
router.include_router(version_router)
router.include_router(mail_router)
router.include_router(documents_router)
router.include_router(integration_router)
router.include_router(audit_log_router)
