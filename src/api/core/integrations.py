from datetime import datetime
from xml.sax.saxutils import escape

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dao.category_dao import CategoryDAO
from src.api.dao.offer_dao import OfferDAO
from src.api.dao.sub_category_dao import SubCategoryDAO


# --------------------------------------------------------
# Helper: build YML as string
# --------------------------------------------------------
async def build_yml(db: AsyncSession) -> str:
    categories = await CategoryDAO.find_all(db, {})
    subcategories = await SubCategoryDAO.find_all(db, {})
    offers = await OfferDAO.find_all(db, {"is_deleted": False})

    # ---------------- Categories ----------------
    categories_xml = []
    for cat in categories:
        categories_xml.append(f'<category id="{cat.id}">{escape(cat.name)}</category>')

    for sub in subcategories:
        categories_xml.append(
            f'<category id="{sub.id}" parentId="{sub.category_id}">{escape(sub.name)}</category>'
        )

    categories_xml = "\n".join(categories_xml)

    # ---------------- Offers ----------------
    offers_xml_list = []

    for offer in offers:
        product = offer.product
        sub = product.sub_category

        # товар недоступен
        if offer.quantity <= 0:
            offers_xml_list.append(
                f'<offer id="{offer.id}" available="false">'
                f"<name>{escape(product.name)}</name>"
                f"<vendor>{escape(offer.brand)}</vendor>"
                f"<vendorCode>{escape(offer.manufacturer_number)}</vendorCode>"
                f"<categoryId>{sub.id}</categoryId>"
                f"<picture>{offer.image_url}</picture>"
                f"<barcode>{offer.sku or ''}</barcode>"
                f"<description><![CDATA[{escape(offer.internal_description or '')}]]></description>"
                f"</offer>"
            )
            continue

        # товар в наличии
        offers_xml_list.append(
            f'<offer id="{offer.id}" available="true">'
            f"<name>{escape(product.name)}</name>"
            f"<vendor>{escape(offer.brand)}</vendor>"
            f"<vendorCode>{escape(offer.manufacturer_number)}</vendorCode>"
            f"<categoryId>{sub.id}</categoryId>"
            f"<picture>{offer.image_url}</picture>"
            f"<price>{offer.price_rub}</price>"
            f"<currencyId>RUB</currencyId>"
            f"<barcode>{offer.sku or ''}</barcode>"
            f"<description><![CDATA[{escape(offer.internal_description or '')}]]></description>"
            f"</offer>"
        )

    offers_xml = "\n".join(offers_xml_list)

    now = datetime.now().isoformat()

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

    return xml
