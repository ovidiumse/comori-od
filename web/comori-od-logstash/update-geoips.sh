#!/bin/sh

GEOIP_DIR=/usr/share/geoipupdate
geoipupdate -f "${GEOIP_DIR}/geoip.conf" -d "${GEOIP_DIR}"