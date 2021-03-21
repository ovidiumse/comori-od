FROM docker.elastic.co/beats/filebeat:7.11.2

USER root
RUN yum -y update && yum -y install less curl

USER filebeat
COPY filebeat-index-template.json .
COPY on-start.sh .
COPY filebeat.yml /usr/share/filebeat/
COPY nginx.yml /usr/share/filebeat/modules.d/

CMD ./on-start.sh