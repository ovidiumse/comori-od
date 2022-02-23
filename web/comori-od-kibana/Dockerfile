ARG ES_VERSION

FROM docker.elastic.co/kibana/kibana:${ES_VERSION}
USER root
RUN apt-get -y update && apt-get -y install less curl vim
USER kibana

COPY kibana.yml /usr/share/kibana/config/
COPY on-start.sh .

CMD ./on-start.sh