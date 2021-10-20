FROM docker.elastic.co/beats/metricbeat:7.15.1

COPY metricbeat.yml /usr/share/metricbeat/metricbeat.yml
USER root
RUN chown root:metricbeat /usr/share/metricbeat/metricbeat.yml
USER metricbeat
COPY on-start.sh .

CMD ./on-start.sh