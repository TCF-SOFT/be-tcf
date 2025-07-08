from src.api.dao.base import BaseDAO
from src.models import Address


class AddressDAO(BaseDAO):
    model = Address
