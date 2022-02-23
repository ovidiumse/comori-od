#!/bin/sh

until curl -u\"${ELASTIC_USER}:${ELASTIC_PASSWORD}\" http://comori-od-es:9200; do
    >&2 echo "Elasticsearch is unavailable, sleeping..."
    sleep 3
done

curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" \
    -XPOST http://comori-od-es:9200/_security/user/${KIBANA_USER}/_password \
    -H "Content-Type: application/json" \
    -d "{\"password\": \"${KIBANA_PASSWORD}\"}"

/usr/local/bin/kibana-docker
