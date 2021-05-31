#!/bin/sh

GEOIP_DIR=/usr/share/geoipupdate

echo "AccountID ${GEOIP_ACCOUNTID}" > "${GEOIP_DIR}/geoip.conf"
echo "LicenseKey ${GEOIP_LICENSEKEY}" >> "${GEOIP_DIR}/geoip.conf"
echo "EditionIDs GeoLite2-City" >> "${GEOIP_DIR}/geoip.conf"

/usr/local/bin/docker-entrypoint -e