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

echo "Fixing Trifa - Oglinda inimii omului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_oglinda_inimii_omului/trifa_oglinda_inimii_omului.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Oglinda inimii omului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_oglinda_inimii_omului/trifa_oglinda_inimii_omului_fixed.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Oglinda inimii omului" \
    -b "Oglinda inimii omului" \
    -e ${DATA_DIR}/trifa_oglinda_inimii_omului/trifa_oglinda_inimii_omului.json

echo "Post-processing Trifa - Oglinda inimii omului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_oglinda_inimii_omului/trifa_oglinda_inimii_omului.json $@

echo "Removing existing Trifa - Oglinda inimii omului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --book "Oglinda inimii omului" $@

echo "Uploading Trifa - Oglinda inimii omului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_oglinda_inimii_omului/trifa_oglinda_inimii_omului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded