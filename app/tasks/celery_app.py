import os

from celery import Celery

CELERY_HOST = os.environ.get("CELERY_HOST", "localhost")
CELERY_PORT = os.environ.get("CELERY_PORT", 6379)
CELERY_URL = f"redis://{CELERY_HOST}:{CELERY_PORT}/0"

celery_app = Celery("LolAnalytics")
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_url = CELERY_URL
celery_app.conf.result_backend = CELERY_URL
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.task_serializer = "json"
celery_app.conf.timezone = "America/Sao_Paulo"


celery_app.autodiscover_tasks(["tasks"])
