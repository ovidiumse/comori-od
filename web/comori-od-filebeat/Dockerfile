ARG ES_VERSION

FROM docker.elastic.co/beats/filebeat:${ES_VERSION}

USER root
RUN apt-get -y update && apt-get -y install less curl

USER filebeat
COPY filebeat-8.0.0.json ./filebeat-index-template.json
COPY filebeat-mappings.json .
COPY on-start.sh .
COPY filebeat.yml /usr/share/filebeat/

CMD ./on-start.sh