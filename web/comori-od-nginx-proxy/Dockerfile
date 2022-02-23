FROM jwilder/nginx-proxy:latest
RUN apt-get update && apt-get install -y less curl
COPY comori-od.conf /etc/nginx/vhost.d/localhost
COPY comori-od.conf /etc/nginx/vhost.d/comori-od.ro
COPY comori-od.conf /etc/nginx/vhost.d/www.comori-od.ro
COPY api.comori-od.conf /etc/nginx/vhost.d/
COPY bible-api.comori-od.conf /etc/nginx/vhost.d/
COPY kibana.comori-od.conf /etc/nginx/vhost.d/
COPY proxy.conf /etc/nginx/conf.d/proxy.conf
COPY nginx.tmpl .
RUN mkdir /usr/share/nginx/html/.well-known
COPY apple-app-site-association /usr/share/nginx/html/.well-known/apple-app-site-association
COPY privacy.html /usr/share/nginx/html/privacy.html
COPY galateni_5_19_6_1_18.html /usr/share/nginx/html/