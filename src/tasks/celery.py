from celery import Celery

from src.config.config import settings

# first argument = name of celery app
celery = Celery(
    "tasks", broker=str(settings.redis_url), include=["src.api.tasks.tasks"]
)
