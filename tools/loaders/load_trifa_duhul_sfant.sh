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

echo "Fixing Trifa - Duhul Sfânt..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_duhul_sfant/trifa_duhul_sfant.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Duhul Sfânt..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_duhul_sfant/trifa_duhul_sfant_fixed.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Duhul Sfânt" \
    -b "Duhul Sfânt" \
    -e ${DATA_DIR}/trifa_duhul_sfant/trifa_duhul_sfant.json

echo "Post-processing Trifa - Duhul Sfânt..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_duhul_sfant/trifa_duhul_sfant.json $@

echo "Removing existing Trifa - Duhul Sfânt using '$@' flags..."
${TOOLS_DIR}/od-remove.py --book "Duhul Sfânt" $@

echo "Uploading Trifa - Duhul Sfânt..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_duhul_sfant/trifa_duhul_sfant_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded