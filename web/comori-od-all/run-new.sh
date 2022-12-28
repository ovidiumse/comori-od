#!/usr/bin/sh

export $(cat .env-new | xargs)
docker compose -f docker-compose-new.yaml --env-file .env-prod up -d $@