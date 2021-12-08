ARG ES_VERSION

FROM docker.elastic.co/kibana/kibana:${ES_VERSION}
USER root
RUN yum -y update && yum -y install less curl
USER kibana
COPY kibana.yml /usr/share/kibana/config/
