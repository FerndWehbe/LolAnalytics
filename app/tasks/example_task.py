from celery import shared_task

from .celery_app import celery_app


@celery_app.task()
def exemplo_task(name):
    return name


@shared_task
def teste_task():
    return "Testando"
