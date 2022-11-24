FROM node:latest as build-stage
ARG buildtype
ARG NODE_OPTIONS
ARG VUE_APP_BASE_URL

ENV NODE_OPTIONS="$NODE_OPTIONS"

WORKDIR /app
COPY package*.json ./
RUN npm install -g npm
RUN npm install
COPY ./ .

RUN echo "${VUE_APP_BASE_URL}" > .env.prod
RUN npm run $buildtype

FROM nginx as production-stage
RUN mkdir /app
COPY --from=build-stage /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf