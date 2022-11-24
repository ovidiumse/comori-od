#!/bin/sh

docker compose -f docker-compose-dev.yaml $@ logs -f --tail=10
