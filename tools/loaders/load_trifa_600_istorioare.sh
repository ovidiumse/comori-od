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

echo "Fixing Trifa - 600 de istorioare..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_600_istorioare/trifa_600_istorioare.htm -c ${CFG_DIR}/trifa_600_istorioare.yaml

echo "Extracting Trifa - 600 de istorioare..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_600_istorioare/trifa_600_istorioare_fixed.htm \
    -c ${CFG_DIR}/trifa_600_istorioare.yaml \
    -a "Pr. Iosif Trifa" \
    -v "600 de istorioare" \
    -b "600 de istorioare" \
    -e ${DATA_DIR}/trifa_600_istorioare/trifa_600_istorioare.json

echo "Post-processing Trifa - 600 de istorioare..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_600_istorioare/trifa_600_istorioare.json $@

echo "Removing existing Trifa - 600 de istorioare using '$@' flags..."
${TOOLS_DIR}/od-remove.py --book "600 de istorioare" $@

echo "Uploading Trifa - 600 de istorioare..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_600_istorioare/trifa_600_istorioare_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded