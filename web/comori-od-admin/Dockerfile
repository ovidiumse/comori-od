FROM node:latest as build-stage
ARG NODE_OPTIONS

ENV NODE_OPTIONS="$NODE_OPTIONS"

WORKDIR /app
COPY package*.json ./
RUN npm install -g npm
RUN npm install
COPY ./ .

RUN npm run build

FROM nginx as production-stage
RUN mkdir /app
COPY --from=build-stage /app/build /app
COPY nginx.conf /etc/nginx/nginx.conf