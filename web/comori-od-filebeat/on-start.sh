#!/bin/sh

until curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-es:9200'; do
    >&2 echo "Elasticsearch is unavailable, sleeping..."
    sleep 3
done

curl -XPUT -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-es:9200/_template/filebeat-7.9.3' -H "Content-Type:application/json" -d@filebeat-index-template.json

until curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-kibana:5601/api/status'; do
    >&2 echo "Kibana is unavailable, sleeping..."
    sleep 3
done

sleep 10

/usr/local/bin/docker-entrypoint -e