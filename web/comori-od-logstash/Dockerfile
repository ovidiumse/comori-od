FROM docker.elastic.co/logstash/logstash:7.9.2
USER root
RUN yum -y update && yum -y install less curl
USER logstash
RUN rm -f /usr/share/logstash/pipeline/logstash.conf
ADD pipeline/ /usr/share/logstash/pipeline/
ADD config/ /usr/share/logstash/config/
ADD patterns/ /etc/logstash/patterns/