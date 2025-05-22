from celery import Celery

from src.config.config import settings

# first argument = name of celery app
celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS.REDIS_HOST}:{settings.REDIS.REDIS_PORT}",
    include=["src.tasks.tasks"],
)
