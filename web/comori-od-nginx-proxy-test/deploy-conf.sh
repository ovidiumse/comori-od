#!/usr/bin/sh

docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/test.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/localhost
docker cp testapi.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testapi.comori-od.ro
docker cp testbible-api.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testbible-api.comori-od.ro
docker cp testmongo.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testmongo.comori-od.ro
docker cp testnew.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testnew.comori-od.ro
docker cp testjupyter.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testjupyter.comori-od.ro
docker cp proxy.conf nginx-proxy:/etc/nginx/conf.d/
docker restart nginx-proxy