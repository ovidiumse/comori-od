#!/usr/bin/sh

export $(cat .env-test | xargs)
docker compose -f docker-compose-test.yaml --env-file .env-prod build $@