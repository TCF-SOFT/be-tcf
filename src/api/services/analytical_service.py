best_selling_query = """SELECT
  p.name,
  SUM(waybill_offers.quantity) AS total_sold
FROM waybills
JOIN waybill_offers ON waybills.id = waybill_offers.waybill_id
JOIN offers o ON waybill_offers.offer_id = o.id
JOIN products p ON o.product_id = p.id
WHERE waybills.is_pending = false and waybills.waybill_type = 'WAYBILL_OUT'
GROUP BY p.name
ORDER BY total_sold DESC;"""
