#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2023-09-12"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Citiri și tâlcuiri din Biblie..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_citiri_si_talcuiri_din_biblie/trifa_citiri_si_talcuiri_din_biblie.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Citiri și tâlcuiri din Biblie..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_citiri_si_talcuiri_din_biblie/trifa_citiri_si_talcuiri_din_biblie_fixed.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Citiri și tâlcuiri din Biblie" \
    -b "Citiri și tâlcuiri din Biblie" \
    -e ${DATA_DIR}/trifa_citiri_si_talcuiri_din_biblie/trifa_citiri_si_talcuiri_din_biblie.json

echo "Post-processing Trifa - Citiri și tâlcuiri din Biblie..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_citiri_si_talcuiri_din_biblie/trifa_citiri_si_talcuiri_din_biblie.json $@

echo "Removing existing Trifa - Citiri și tâlcuiri din Biblie using '$@' flags..."
${TOOLS_DIR}/od-remove.py --book "Citiri și tâlcuiri din Biblie" $@

echo "Uploading Trifa - Citiri și tâlcuiri din Biblie..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_citiri_si_talcuiri_din_biblie/trifa_citiri_si_talcuiri_din_biblie_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded