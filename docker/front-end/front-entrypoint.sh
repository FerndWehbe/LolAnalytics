#!/bin/sh

until cd /app
do
    echo "Waiting for server volume..."
done

until npm run generate
do
    echo "Witing for nuxt generate..."
done

until npm run build
do
    echo "Witing for nuxt build..."
done

npm start --prefix /app