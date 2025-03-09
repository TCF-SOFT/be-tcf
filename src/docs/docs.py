from pydantic import BaseModel, ConfigDict

servers = [
    {"url": "http://127.0.0.1:8080", "description": "Local environment"},
    {
        "url": "https://api.dev.alpha-analytics.dev/v2/pricingv2/predict_price",
        "description": "Development environment",
    },
    {
        "url": "https://api.stage.alpha-analytics.dev/v2/pricingv2/predict_price",
        "description": "Staging environment",
    },
    {
        "url": "https://api.prod.alpha-analytics.dev/v2/pricingv2/predict_price",
        "description": "Production environment",
    },
]

title = "TCF API"
description = """
## How to use this API
lore ipsum dolor sit amet consectetur adipiscing elit

## Available ENUMs
lore ipsum dolor sit amet consectetur adipiscing elit
"""
summary = "API to calculate the predicted price for a vehicle with given features"

contact = {
    "name": "Vadym Tatarinov",
    "url": "https://ford-parts.com.ru",
    "email": "utikpuhlik@protonmail.ch",
}


class HTTPError(BaseModel):
    detail: str = "Oops! Not enough similar cars on the market to estimate price. Please contact support."
    model_config = ConfigDict(json_schema_extra={"example": {"detail": detail}})


responses_pricing = {
    400: {"description": "Bad Request", "model": HTTPError},
}
