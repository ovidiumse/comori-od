ARG ES_VERSION

FROM docker.elastic.co/logstash/logstash:${ES_VERSION}
USER root
RUN apt-get -y update && apt-get -y install less curl vim wget

ARG GEOIP_DIR=/usr/share/geoipupdate
ARG GEOIP_VER=4.8.0
ARG GEOIP_PACKAGE=geoipupdate_${GEOIP_VER}_linux_amd64.deb

RUN mkdir -p ${GEOIP_DIR}
RUN chown -R logstash ${GEOIP_DIR}
RUN wget "https://github.com/maxmind/geoipupdate/releases/download/v${GEOIP_VER}/${GEOIP_PACKAGE}" -P "${GEOIP_DIR}"
RUN apt install "${GEOIP_DIR}/${GEOIP_PACKAGE}"

USER logstash
COPY on-start.sh .
COPY update-geoips.sh .
COPY GeoLite2-City.mmdb "${GEOIP_DIR}/"

RUN rm -f /usr/share/logstash/pipeline/logstash.conf
ADD pipeline/ /usr/share/logstash/pipeline/
ADD config/ /usr/share/logstash/config/
ADD patterns/ /etc/logstash/patterns/

CMD ./on-start.sh