#!/bin/sh

docker compose -f docker-compose-devall.yaml $@ logs -f --tail=10
