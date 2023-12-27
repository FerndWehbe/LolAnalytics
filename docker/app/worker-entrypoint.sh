#!/bin/sh


until cd /app/app
do
    echo "Waiting for server volume..."
done

celery -A tasks.celery_app worker -E --loglevel=info --concurrency=2