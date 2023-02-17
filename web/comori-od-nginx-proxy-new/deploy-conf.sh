#!/usr/bin/sh

export $(cat ../comori-od-all/.env-new | xargs)
docker cp new.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/new.comori-od.ro
docker cp new.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/localhost
docker cp newapi.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/newapi.comori-od.ro
docker cp newbible-api.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/newbible-api.comori-od.ro
docker cp newmongo.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/newmongo.comori-od.ro
docker cp newnew.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/newnew.comori-od.ro
docker cp proxy.conf nginx-proxy:/etc/nginx/conf.d/
docker cp nginx.tmpl nginx-proxy:/app/

docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/test.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testapi.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testbible-api.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testjupyter.comori-od.ro
docker cp test.comori-od.conf nginx-proxy:/etc/nginx/vhost.d/testmongo.comori-od.ro
docker restart nginx-proxy