FROM docker.elastic.co/logstash/logstash:7.15.0
USER root
RUN yum -y update && yum -y install less curl vim wget

ARG GEOIP_DIR=/usr/share/geoipupdate
ARG GEOIP_PACKAGE=geoipupdate_4.5.0_linux_amd64.rpm

RUN mkdir -p ${GEOIP_DIR}
RUN chown -R logstash ${GEOIP_DIR}
RUN wget "https://github.com/maxmind/geoipupdate/releases/download/v4.5.0/${GEOIP_PACKAGE}" -P "${GEOIP_DIR}"
RUN rpm -Uvhi "${GEOIP_DIR}/${GEOIP_PACKAGE}"

USER logstash
COPY on-start.sh .
COPY update-geoips.sh .
COPY GeoLite2-City.mmdb "${GEOIP_DIR}/"

RUN rm -f /usr/share/logstash/pipeline/logstash.conf
ADD pipeline/ /usr/share/logstash/pipeline/
ADD config/ /usr/share/logstash/config/
ADD patterns/ /etc/logstash/patterns/

CMD ./on-start.sh