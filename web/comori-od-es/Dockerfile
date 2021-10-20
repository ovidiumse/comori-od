FROM docker.elastic.co/elasticsearch/elasticsearch:7.15.1
RUN yum -y update && yum -y install less curl

COPY --chown=elasticsearch:elasticsearch elasticsearch.yml /usr/share/elasticsearch/config/