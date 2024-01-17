#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2024-01-15"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Fricoșii..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_fricosii/trifa_fricosii.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Fricoșii..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_fricosii/trifa_fricosii.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Fricoșii" \
    -b "Fricoșii" \
    -e ${DATA_DIR}/trifa_fricosii/trifa_fricosii.json

echo "Post-processing Trifa - Fricoșii..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_fricosii/trifa_fricosii.json $@

echo "Removing existing Trifa - Fricoșii using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Fricoșii" $@

echo "Uploading Trifa - Fricoșii..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_fricosii/trifa_fricosii_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded