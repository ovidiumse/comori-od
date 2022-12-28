#!/usr/bin/sh

export $(cat ../comori-od-all/.env-remote | xargs)
docker compose up -d