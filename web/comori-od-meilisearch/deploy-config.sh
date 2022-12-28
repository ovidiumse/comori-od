#!/usr/bin/sh

docker cp ./config.toml comori-od-meilisearch:/meili_data/
docker restart comori-od-meilisearch