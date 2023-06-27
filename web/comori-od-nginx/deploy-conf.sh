#!/usr/bin/sh

docker exec nginx-proxy-manager bash -c "mkdir -p /static/comori-od-static-vue/html/.well-known"
docker cp apple-app-site-association nginx-proxy-manager:/static/comori-od-static-vue/html/.well-known/apple-app-site-association
docker cp assetlinks.json nginx-proxy-manager:/static/comori-od-static-vue/html/.well-known/assetlinks.json
docker cp privacy.html nginx-proxy-manager:/static/comori-od-static-vue/html/privacy.html
