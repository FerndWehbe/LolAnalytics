#!/bin/sh

until cd /app/app
do
    echo "Waiting for server volume..."
done

python main.py