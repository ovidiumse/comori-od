#!/usr/bin/sh

docker cp comori-od.conf nginx-proxy:/etc/nginx/vhost.d/comori-od.ro
docker cp comori-od.conf nginx-proxy:/etc/nginx/vhost.d/www.comori-od.ro
docker cp api.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/api.comori-od.ro
docker cp bible-api.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/bible-api.comori-od.ro
docker cp mongo.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/mongo.comori-od.ro
docker cp new.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/

docker cp proxy.conf nginx-proxy:/etc/nginx/conf.d/
docker cp nginx.tmpl nginx-proxy:/app/

docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/test.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testapi.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testbible-api.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testjupyter.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testmongo.comori-od.ro
docker restart nginx-proxy