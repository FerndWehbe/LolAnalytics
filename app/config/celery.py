from celery import Celery, Task

from .config import CELERY_URL


class CeleryTaskBase(Task):
    abstract = True


celery_app = Celery("LolAnalytics")
celery_app.conf.broker_url = CELERY_URL
celery_app.conf.result_backend = CELERY_URL
celery_app.conf.result_serializer = "json"
celery_app.conf.task_serializer = "json"
celery_app.conf.worker_concurrency = 2
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.autodiscover_tasks(["app.tasks"])

celery_app.Task = CeleryTaskBase
