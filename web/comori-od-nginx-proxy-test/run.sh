#!/usr/bin/sh

export $(cat ../comori-od-all/.env-test | xargs)
docker compose up -d