#!/bin/sh

/usr/local/bin/docker-entrypoint.sh &

until curl http://localhost:9200; do
    >&2 echo "Elasticsearch is unavailable, sleeping..."
    sleep 3
done

curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" -XPOST http://localhost:9200/_security/user/${LOGSTASH_USER}/_password -H "Content-Type: application/json" -d '{"password": "${KIBANA_PASSWORD}"}'
