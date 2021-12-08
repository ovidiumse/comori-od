ARG ES_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ES_VERSION}
RUN apt-get -y update && apt-get -y install less curl

COPY --chown=elasticsearch:elasticsearch elasticsearch.yml /usr/share/elasticsearch/config/