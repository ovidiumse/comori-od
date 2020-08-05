FROM jwilder/nginx-proxy
RUN apt-get update && apt-get install -y less curl
COPY comori-od.conf /etc/nginx/vhost.d/localhost
COPY comori-od.conf /etc/nginx/vhost.d/comori-od.ro
COPY comori-od.conf /etc/nginx/vhost.d/www.comori-od.ro
COPY proxy.conf /etc/nginx/conf.d/proxy.conf
COPY apple-app-site-association /usr/share/nginx/html/apple-app-site-association
