#!/bin/sh

export $(cat .env-remote | xargs)
docker compose -f docker-compose-prod.yaml logs -f --tail=10 
