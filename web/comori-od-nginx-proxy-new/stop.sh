#!/usr/bin/sh

export $(cat ../comori-od-all/.env-new | xargs)
docker compose stop