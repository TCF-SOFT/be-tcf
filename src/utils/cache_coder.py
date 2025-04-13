from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi_cache import Coder
from orjson import orjson


class ORJsonCoder(Coder):
    """
    ORJson Coder for FastAPI Cache
    As we're working with numpy arrays, we need to serialize them as well
    Default json.dumps does not support numpy arrays
    So we use orjson to serialize/deserialize numpy arrays as well
    """

    @classmethod
    def encode(cls, value: Any) -> bytes:
        return orjson.dumps(
            value,
            default=jsonable_encoder,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )

    @classmethod
    def decode(cls, value: bytes) -> Any:
        return orjson.loads(value)
