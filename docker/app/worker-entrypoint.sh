#!/bin/sh


until cd /app
do
    echo "Waiting for server volume..."
done

celery -A app.config.celery_app worker -E --loglevel=info