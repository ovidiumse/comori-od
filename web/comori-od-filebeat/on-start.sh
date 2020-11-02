#!/bin/sh

until curl http://comori-od-es:9200; do
    >&2 echo "Elasticsearch is unavailable, sleeping..."
    sleep 3
done

curl -XPUT 'http://comori-od-es:9200/template/filebeat' -d@filebeat-index-template.json

/usr/local/bin/docker-entrypoint -e