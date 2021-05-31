FROM redis:latest

ARG CONF_PATH=/usr/local/etc/redis/redis.conf

RUN apt-get update && \
    apt-get -y install curl wget less

COPY redis.conf ${CONF_PATH}

CMD redis-server "${CONF_PATH}" --requirepass "${REDIS_PASSWORD}"
