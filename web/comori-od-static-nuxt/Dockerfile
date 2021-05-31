FROM node:lts as build-stage

ARG buildtype
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY ./ .
RUN npm run $buildtype

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

CMD ["npm", "start"]