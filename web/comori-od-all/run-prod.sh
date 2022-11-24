#!/usr/bin/sh

export $(cat .env-remote | xargs)
docker compose -f docker-compose-prod.yaml --env-file .env-prod up -d