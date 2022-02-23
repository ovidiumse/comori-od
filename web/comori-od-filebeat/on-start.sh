#!/bin/sh

until curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-es:9200'; do
    >&2 echo "Elasticsearch is unavailable, sleeping..."
    sleep 3
done

curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" -XDELETE 'http://comori-od-es:9200/filebeat*'
curl -XPUT -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-es:9200/_index_template/filebeat' -H "Content-Type:application/json" -d@filebeat-index-template.json
curl -XPUT -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-es:9200/filebeat' -H "Content-Type:application/json" -d@filebeat-mappings.json

until curl -u"${ELASTIC_USER}:${ELASTIC_PASSWORD}" 'http://comori-od-kibana:5601/api/status'; do
    >&2 echo "Kibana is unavailable, sleeping..."
    sleep 3
done

sleep 10

/usr/local/bin/docker-entrypoint -e