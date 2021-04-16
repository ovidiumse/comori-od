#!/usr/bin/sh

echo "Starting services..."
docker-compose -f docker-compose-dev.yaml --env-file .env-dev up -d
if [ "$1" != "all" ]; then
    echo "Stopping extra (optional) services..."
    docker stop comori-od-filebeat comori-od-logstash comori-od-metricbeat comori-od-kibana
fi