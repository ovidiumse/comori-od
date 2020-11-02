FROM jwilder/nginx-proxy
RUN apt-get update && apt-get install -y less curl
COPY comori-od.conf /etc/nginx/vhost.d/localhost
COPY comori-od.conf /etc/nginx/vhost.d/comori-od.ro
COPY comori-od.conf /etc/nginx/vhost.d/www.comori-od.ro
COPY api.comori-od.conf /etc/nginx/vhost.d/
COPY bibleapi.comori-od.conf /etc/nginx/vhost.d/
COPY kibana.comori-od.conf /etc/nginx/vhost.d/
COPY proxy.conf /etc/nginx/conf.d/proxy.conf
RUN mkdir /usr/share/nginx/html/.well-known
COPY apple-app-site-association /usr/share/nginx/html/.well-known/apple-app-site-association
