from fastapi_users.authentication import BearerTransport

# Transport (bearer / cookie) + Strategy (JWT / Redis / DB) = Authentication backend
bearer_transport = BearerTransport(tokenUrl="auth/login")
