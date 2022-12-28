#!/usr/bin/sh

DOCKER_BUILDKIT=1
export $(cat ../comori-od-all/.env-test | xargs)
docker compose build