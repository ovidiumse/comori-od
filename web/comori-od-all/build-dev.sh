#!/usr/bin/sh

docker compose -f docker-compose-dev.yaml --env-file .env-dev build $@