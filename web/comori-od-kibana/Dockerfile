FROM docker.elastic.co/kibana/kibana:7.15.0
USER root
RUN yum -y update && yum -y install less curl
USER kibana
COPY kibana.yml /usr/share/kibana/config/
