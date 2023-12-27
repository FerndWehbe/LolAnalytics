FROM node:lts-alpine

WORKDIR /app

ADD ./front-end/package.json /app/
ADD ./front-end/package-lock.json /app/
RUN npm install

ADD ./front-end /app/
ADD ./docker /app/docker