ARG ES_VERSION

FROM docker.elastic.co/beats/metricbeat:${ES_VERSION}

COPY metricbeat.yml /usr/share/metricbeat/metricbeat.yml

USER root
RUN chown root:metricbeat /usr/share/metricbeat/metricbeat.yml
USER metricbeat
COPY on-start.sh .

CMD ./on-start.sh