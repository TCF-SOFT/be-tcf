from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .address_router import router as address_router
from .analytical_router import router as analytical_router
from .category_router import router as category_router
from .documents_router import router as documents_router
from .health_check_router import router as health_check_router
from .mail_router import router as mail_router
from .offer_router import router as offer_router
from .order_offers_router import router as order_offers_router
from .order_router import router as order_router
from .product_router import router as product_router
from .sub_category_router import router as sub_category_router
from .user_router import router as user_router
from .version_router import router as version_router
from .waybill_offers_router import router as waybill_offers_router
from .waybill_router import router as waybill_router
from .webhook_router import router as webhook_router

# TODO: add v1 prefix

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(dependencies=[Depends(http_bearer)])

# Include all routers
router.include_router(user_router)
router.include_router(category_router)
router.include_router(sub_category_router)
router.include_router(product_router)
router.include_router(offer_router)
router.include_router(waybill_router)
router.include_router(waybill_offers_router)
router.include_router(order_router)
router.include_router(order_offers_router)
router.include_router(analytical_router)
router.include_router(address_router)
router.include_router(webhook_router)
router.include_router(health_check_router)
router.include_router(version_router)
router.include_router(mail_router)
router.include_router(documents_router)
