#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2024-01-16"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Biblia - Cartea Vieții..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_biblia_cartea_vietii/trifa_biblia_cartea_vietii.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Biblia - Cartea Vieții..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_biblia_cartea_vietii/trifa_biblia_cartea_vietii.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Biblia - Cartea Vieții" \
    -b "Biblia - Cartea Vieții" \
    -e ${DATA_DIR}/trifa_biblia_cartea_vietii/trifa_biblia_cartea_vietii.json

echo "Post-processing Trifa - Biblia - Cartea Vieții..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_biblia_cartea_vietii/trifa_biblia_cartea_vietii.json $@

echo "Removing existing Trifa - Biblia - Cartea Vieții using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Biblia - Cartea Vieții" $@

echo "Uploading Trifa - Biblia - Cartea Vieții..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_biblia_cartea_vietii/trifa_biblia_cartea_vietii_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded