from io import BytesIO
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from schemas.waybill_offer_schema import WaybillOfferSchema
from schemas.waybill_schema import WaybillSchema

templates_path = Path("templates")

def generate_waybill_word(waybill: WaybillSchema, offers: list[WaybillOfferSchema], total_sum):
    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Arial"
    font.size = Pt(11)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")

    doc.add_heading(f"Накладная № {waybill['number']}", level=1)

    doc.add_paragraph(f"ФИО: {waybill['manager_name']}")
    doc.add_paragraph(f"Телефон: {waybill['phone']}")
    doc.add_paragraph(f"Город: {waybill.get('city', 'Не заполнен у пользователя')}")
    doc.add_paragraph(f"Доставка: {waybill.get('delivery', 'Не указано')}")
    doc.add_paragraph("")

    table = doc.add_table(rows=1, cols=7)
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "#"
    hdr_cells[1].text = "Категория"
    hdr_cells[2].text = "Наименование"
    hdr_cells[3].text = "Бренд"
    hdr_cells[4].text = "Номер"
    hdr_cells[5].text = "Цена"
    hdr_cells[6].text = "Кол-во / Сумма"

    for i, item in enumerate(offers, 1):
        row_cells = table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = item.get("category", "")
        row_cells[2].text = item["product_name"]
        row_cells[3].text = item["brand"]
        row_cells[4].text = item["manufacturer_number"]
        row_cells[5].text = f"{item['price_rub']:.0f} руб."
        row_cells[
            6
        ].text = f"{item['quantity']} × {item['price_rub']:.0f} = {item['price_rub'] * item['quantity']:.0f} руб."

    doc.add_paragraph("")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"Итого: {total_sum:.0f} руб.").bold = True

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()
