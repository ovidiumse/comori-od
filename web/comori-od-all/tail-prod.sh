#!/bin/sh

docker-compose --context comori-od -f docker-compose-prod.yaml logs -f --tail=10 
