ARG ES_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ES_VERSION}

USER root
RUN apt-get -y update && apt-get -y install less curl
USER elasticsearch
COPY --chown=elasticsearch:elasticsearch elasticsearch.yml /usr/share/elasticsearch/config/