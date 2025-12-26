from enum import StrEnum


class ShippingMethod(StrEnum):
    SELF_PICKUP = "SELF_PICKUP"
    CARGO = "CARGO"
    OTHER = "OTHER"


class OrderStatus(StrEnum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPING = "SHIPPING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class CustomerType(StrEnum):
    USER_RETAIL = "USER_RETAIL"
    USER_WHOLESALE = "USER_WHOLESALE"
    USER_SUPER_WHOLESALE = "USER_SUPER_WHOLESALE"


class WaybillType(StrEnum):
    WAYBILL_IN = "WAYBILL_IN"
    WAYBILL_OUT = "WAYBILL_OUT"
    WAYBILL_RETURN = "WAYBILL_RETURN"


class UserBalanceChangeReason(StrEnum):
    WAYBILL_PAYMENT = "WAYBILL_PAYMENT"
    ADMIN_ADJUSTMENT = "ADMIN_ADJUSTMENT"
    PROMOTION_CREDIT = "PROMOTION_CREDIT"
    OTHER = "OTHER"


class Currency(StrEnum):
    """
    ISO 4217 Currency Codes
    """

    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    TRY = "TRY"


class Role(StrEnum):
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"
    USER = "USER"


ROLE_HIERARCHY = {
    Role.USER: 1,
    Role.EMPLOYEE: 2,
    Role.ADMIN: 3,
}


class PriceListExt(StrEnum):
    EXCEL = "xlsx"
    CSV = "csv"


class PriceListType(StrEnum):
    RETIAL = "retail"
    WHOLESALE = "wholesale"
