from datetime import date

from pydantic import BaseModel, constr
from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber


class Card(BaseModel):
    """
    https://docs.pydantic.dev/2.0/usage/types/extra_types/payment_cards/
    """

    name: constr(strip_whitespace=True, min_length=1)
    number: PaymentCardNumber
    exp: date

    @property
    def brand(self) -> PaymentCardBrand:
        return self.number.brand

    @property
    def expired(self) -> bool:
        return self.exp < date.today()


# card = Card(
#     name='Georg Wilhelm Friedrich Hegel',
#     number='2200 0202 2774 2100',
#     exp=date(2023, 9, 30),
# )
