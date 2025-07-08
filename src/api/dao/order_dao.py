from src.api.dao.base import BaseDAO
from src.models import Order


class OrderDAO(BaseDAO):
    model = Order