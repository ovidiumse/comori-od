#!/usr/bin/sh

docker-compose --context comori-od -f docker-compose-prod.yaml --env-file .env-prod up -d