#!/usr/bin/sh

export $(cat ../comori-od-all/.env-remote | xargs)
docker cp comori-od.conf nginx-proxy:/etc/nginx/vhost.d/comori-od.ro
docker cp comori-od.conf nginx-proxy:/etc/nginx/vhost.d/localhost
docker cp comori-od.conf nginx-proxy:/etc/nginx/vhost.d/www.comori-od.ro
docker cp api.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/api.comori-od.ro
docker cp bible-api.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/bible-api.comori-od.ro
docker cp mongo.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/mongo.comori-od.ro
docker cp kibana.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/kibana.comori-od.ro
docker cp grafana.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/grafana.comori-od.ro
docker cp proxy.conf nginx-proxy:/etc/nginx/conf.d/
docker restart nginx-proxy
