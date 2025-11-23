import datetime
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Response
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.category_dao import CategoryDAO
from src.api.dao.offer_dao import OfferDAO
from src.api.dao.sub_category_dao import SubCategoryDAO
from src.api.di.db_helper import db_helper
from src.utils.cache_coder import ORJsonCoder

router = APIRouter(tags=["Integrations"], prefix="/integrations")


@cache(expire=3600 * 12, coder=ORJsonCoder)
@router.get("/yml", response_class=Response)
async def export_yml(db: AsyncSession = Depends(db_helper.session_getter)):
    """
    Export YML for Yandex.Market
    """

    # --------------------------------------------------------
    # Load all data
    # --------------------------------------------------------
    categories = await CategoryDAO.find_all(db, {})
    subcategories = await SubCategoryDAO.find_all(db, {})
    offers = await OfferDAO.find_all(db, {"is_deleted": False})

    # --------------------------------------------------------
    # Build <categories>
    # --------------------------------------------------------
    categories_xml = []

    # Parent categories
    for cat in categories:
        categories_xml.append(f'<category id="{cat.id}">{escape(cat.name)}</category>')

    # Subcategories (with parentId)
    for sub in subcategories:
        categories_xml.append(
            f'<category id="{sub.id}" parentId="{sub.category_id}">{escape(sub.name)}</category>'
        )

    categories_xml = "\n".join(categories_xml)

    # --------------------------------------------------------
    # Build <offers>
    # --------------------------------------------------------
    offers_xml_list = []

    for offer in offers:
        product = offer.product
        sub = product.sub_category

        offers_xml_list.append(f"""
        <offer id="{offer.id}">
            <name>{escape(product.name)}</name>
            <vendor>{escape(offer.brand)}</vendor>
            <vendorCode>{escape(offer.manufacturer_number)}</vendorCode>
            <categoryId>{sub.id}</categoryId>
            <picture>{offer.image_url}</picture>
            <price>{offer.price_rub}</price>
            <currencyId>RUB</currencyId>
            <quantity>{offer.quantity}</quantity>
            <barcode>{offer.sku or ""}</barcode>
            <description><![CDATA[{escape(offer.internal_description or "")}]]></description>
        </offer>
        """)

    offers_xml = "\n".join(offers_xml_list)

    # --------------------------------------------------------
    # Final XML
    # --------------------------------------------------------
    now = datetime.datetime.now().isoformat()

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="{now}">
    <shop>
        <name>Торговый центр Ford</name>
        <company>Торговый центр Ford | TCF</company>
        <url>https://ford-parts.com.ru</url>

        <categories>
            {categories_xml}
        </categories>

        <offers>
            {offers_xml}
        </offers>
    </shop>
</yml_catalog>
"""

    return Response(content=xml, media_type="application/xml")
