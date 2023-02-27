#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2021-05-31"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Spre Canaan..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_spre_canaan/trifa_spre_canaan.htm -c ${CFG_DIR}/trifa_spre_canaan.yaml

echo "Extracting Trifa - Spre Canaan..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_spre_canaan/trifa_spre_canaan_fixed.htm \
    -c ${CFG_DIR}/trifa_spre_canaan.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Spre Canaan" \
    -b "Spre Canaan" \
    -e ${DATA_DIR}/trifa_spre_canaan/trifa_spre_canaan.json

echo "Post-processing Trifa - Spre Canaan..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_spre_canaan/trifa_spre_canaan.json $@ -s

echo "Removing existing Trifa - Spre Canaan using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Spre Canaan" $@

echo "Uploading Trifa - 30 de carti..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_spre_canaan/trifa_spre_canaan_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded