FROM node:lts as build-stage

ARG buildtype
ARG NODE_OPTIONS

WORKDIR /app
COPY package*.json ./

ENV NODE_OPTIONS="$NODE_OPTIONS"
RUN npm install

COPY ./ .
RUN npm run $buildtype

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3001

CMD ["npm", "start"]