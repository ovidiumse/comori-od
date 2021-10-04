#!/usr/bin/sh

docker-compose --context comori-od -f docker-compose-beta.yaml --env-file .env-prod build $@