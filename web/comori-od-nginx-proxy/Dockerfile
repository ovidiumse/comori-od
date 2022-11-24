FROM jwilder/nginx-proxy:latest
RUN apt-get update && apt-get install -y less curl vim
COPY comori-od.conf /etc/nginx/vhost.d/localhost
COPY comori-od.conf /etc/nginx/vhost.d/comori-od.ro
COPY comori-od.conf /etc/nginx/vhost.d/www.comori-od.ro
COPY api.comori-od.conf /etc/nginx/vhost.d/api.comori-od.ro
COPY bible-api.comori-od.conf /etc/nginx/vhost.d/bible-api.comori-od.ro
COPY kibana.comori-od.conf /etc/nginx/vhost.d/kibana.comori-od.ro
COPY proxy.conf /etc/nginx/conf.d/proxy.conf
COPY nginx.tmpl .

# Apple
RUN mkdir /usr/share/nginx/html/.well-known
COPY apple-app-site-association /usr/share/nginx/html/.well-known/apple-app-site-association

# Privacy
COPY privacy.html /usr/share/nginx/html/privacy.html

# Prepare nginx static json directories
RUN mkdir -p /usr/share/nginx/html/od/data
RUN mkdir -p /usr/share/nginx/html/odbeta/data