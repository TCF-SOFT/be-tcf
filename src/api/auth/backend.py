from fastapi_users.authentication import AuthenticationBackend

from src.api.auth.strategy import get_database_strategy
from src.api.auth.transport import bearer_transport

authentication_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
