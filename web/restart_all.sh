#!/usr/bin/sh

cd comori-od-all
docker-compose down --volume
cd ../comori-od-nginx-proxy
docker-compose down --volume

docker ps

docker-compose build
docker-compose up -d
cd ../comori-od-all
docker-compose up -d

docker ps
