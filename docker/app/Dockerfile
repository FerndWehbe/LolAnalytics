FROM python:3.11.5-alpine

RUN apk update && apk add python3-dev gcc libc-dev

WORKDIR /app

RUN pip install --upgrade pip
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt


ADD ./app /app/app
ADD ./docker /app/docker