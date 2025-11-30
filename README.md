# TCF Back-end API

## Table of Contents


## Overview
### Services Layer
- Postgres - main database (sqlalchemy, alembic, asyncpg)
- Redis - cache, async tasks, etc.
- S3 - file storage for assets (aioboto3)
- SMTP - email service (aiosmtplib)

### API Layer
* `dao` - data access objects, used to interact with the database.
* `services` - business logic, used to interact with the `dao` layer and perform operations on the data.
* `common/deps` - common dependencies, used to inject dependencies into the API endpoints.
* `common/services` - common services: redis, S3, etc. Used in `deps` layer.
* `common/microservices` - common microservices: openai
* `pagination` - using ``fastapi_pagination`` for paginated responses, modified in `utils/pagination`.
### API Endpoints
Endpoints such as `/categories`, `/sub-categories`, `/products`, `/offers` are using the same flow:
```mermaid
sequenceDiagram
    title API Flow for GET Requests
    actor User
    participant Router
    participant Redis as Cache
    participant DAO
    participant Postgres as DB

    User->>+Router: GET /categories
    Router->>+Redis: Check cache for categories
    alt is cached
        Redis-->>-Router: Return cached categories
        Router-->>-User: Return categories from cache
    else not cached
        Router->>+DAO: Fetch categories from DB
        DAO->>+Postgres: Query categories
        Postgres-->>-DAO: Return categories
        DAO-->>-Router: Return categories
        Router->>Redis: Cache categories
        Router-->>User: Return categories
    end
```

```mermaid
---
title: API Flow for POST Requests
---
graph LR
    A[Client] --> B[API POST /categories]
    B --> C[Validate input]
    C --> D[Upload image to S3]
    D --> E[Save Entity to DB]
    E --> F[Return created entity]
```

PATCH:
```mermaid
---
title: API Flow for PATCH Requests
---
graph LR
    A[Client] --> B[API PATCH /categories]
    B --> C1[Validate input]
    C1 --> C{Image was sent?}
    C -- Yes --> D[Save image to S3]
    D --> E[Update DB with image URL]
    C -- No --> F[Update DB without image]
    F --> G[Return updated category]

```

DELETE:
```mermaid
sequenceDiagram
    title API Flow for DELETE Requests
    actor User
    participant Router
    participant DAO
    participant Postgres as DB

    User->>+Router: DELETE /categories/{id}
    Router->>+DAO: Delete category from DB
    DAO->>+Postgres: Delete category by ID
    alt category exists
        Postgres-->>-DAO: Return true
        DAO-->>-Router: Return true
        Router-->>User: Return 204 success
    else category not found
        Postgres-->>DAO: Return false
        DAO-->>Router: Return false
        Router-->>User: Return 404 not found
    end
```

### Waybills


### Cart, Orders, and Payments




## DB Schema
```mermaid
---
title: TCF Back-end API Database Schema
---
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_OFFER : contains
    ORDER_OFFER }|--|| OFFER : includes

    USER ||--o{ CART : has
    CART ||--o{ CART_OFFER : contains
    CART_OFFER }|--|| OFFER : includes

    USER ||..|{ ADDRESS : uses

    USER ||--o{ WAYBILL : has
    WAYBILL ||--o{ WAYBILL_OFFER : contains
    WAYBILL_OFFER }|--|| OFFER : includes

    CATEGORY ||--o{ SUBCATEGORY : contains
    SUBCATEGORY ||--o{ PRODUCT : contains
    PRODUCT ||--o{ OFFER : has

```

### Project Structure with C4


### Deployment Diagram for BE
```mermaid
graph TD
    dev[Developer] -->|Push| github[GitHub Repo]

  github --> github_actions[GitHub Actions]
  github_actions -->|Lint/Test/Build| dockerhub[(Docker Hub)]
  dockerhub -->|Image pull| helm[Helm Charts]
  helm -->|Install/Upgrade| k8s[Kubernetes Cluster]

  subgraph "Kubernetes Cluster"
    traefik[Traefik Ingress Controller]
    app_pods(((fa:fa-gear FastAPI App\n  2 replicas)))
    traefik --> app_pods
  end
  app_pods -->|Query| external_postgres
  app_pods -->|Cache| external_redis
  app_pods -->|Assets| s3[(S3 Bucket)]
  app_pods -->|Documents| docx3R((Docx3R\nDocument Service\nPDF, DOCX, XLSX))

 subgraph "External Services - DB VPS"
     external_postgres[(Postgres)]
     external_redis[(Redis)]
 end

  rolling[RollingUpdate:\nmaxSurge=1\nmaxUnavailable=1]
  rolling --- app_pods

  style app_pods fill:#dfd,stroke:#333
  style external_postgres fill:#cde,stroke:#333
  style external_redis fill:#fdd,stroke:#333
  style rolling fill:#eee,stroke:#999,stroke-dasharray: 5 5

```

### Background jobs
1. Celery Stack: celery, redis, flower - complex
2. FastAPI Stack: background tasks, [fastapi mail](https://sabuhish.github.io/fastapi-mail/getting-started/#:~:text=,the%20mail%20defaults%20to%20plain) - simple (using)
3. Dramatiq [link](https://dramatiq.io/guide.html) - simple



## Installation
1. Clone the repository
2. Create a VENV and install packages with UV, python 3.12+
    ```bash
   uv sync --python 3.12
   ```
3. Create a `.env` file in the root directory and add the required environment variables. You can use the `.env.example` as a reference.


## Tests
### General
For infrastructure mock we're using the GitHub `services` to run the dependencies services (Postgres, Redis, S3, SMTP) in a containerized environment.
### Running
To run the tests, execute the following command from the root directory:
```bash
docker compose up -d
coverage run -m pytest -s tests
OR
uv run pytest
```

### Install pre-commit hooks (Linters, formatters, etc.)
```bash
$ pre-commit install
```
And run the hooks on all files (optional), automatically run on every commit:
```bash
$ pre-commit run --all-files
```

## What's new?
### Async DB and DAOs
1. 2 clients: with async with and default one where add commit is allowed
2. Service Layer - business logic
3. DAO unification (TODO)

### HTTP
Formats:
```
1. multipart/form-data - Files (no header)
2. application/x-www-form-urlencoded - Data from forms
3. application/json - JSON (could be header)
```

Working with `multipart/form-data` in FastAPI:
```python
async def post_category(
    payload: Annotated[
        CategoryPostSchema, Depends(CategoryPostSchema.as_form)
    ]
):
    return payload
```
Pydantic:
```python
class CategoryPostSchema(_CategoryBaseSchema):
    @classmethod
    def as_form(cls, name: Annotated[str, Form(...)]) -> "CategoryPostSchema":
        return cls(name=name)
```

HTTPX:
```python
async def test_post_category_creates_category(self, auth_client: AsyncClient):
    auth_client.headers.pop("Content-Type", None)
    files = {
        "image_blob": (
            "candles.webp",
            self.image_blob,
            "image/webp",
        ),
        "name": (None, "candles test category", "text/plain"),
    }


res = await auth_client.post("/categories", files=files)
```
