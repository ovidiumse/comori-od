FROM bugficks/nginx-proxy:latest

RUN apt-get update && apt-get install -y less curl vim
COPY nginx.tmpl .

# Apple
RUN mkdir /usr/share/nginx/html/.well-known
COPY apple-app-site-association /usr/share/nginx/html/.well-known/apple-app-site-association

# Privacy
COPY privacy.html /usr/share/nginx/html/privacy.html

# Prepare nginx static json directories
RUN mkdir -p /usr/share/nginx/html/od/data
RUN mkdir -p /usr/share/nginx/html/od/img
RUN mkdir -p /usr/share/nginx/html/odbeta/data
RUN mkdir -p /usr/share/nginx/html/odbeta/img