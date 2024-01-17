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

echo "Fixing Trifa - Tâlcuirea Evangheliilor..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_talcuirea_evangheliilor/trifa_talcuirea_evangheliilor.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Tâlcuirea Evangheliilor..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_talcuirea_evangheliilor/trifa_talcuirea_evangheliilor.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Tâlcuirea Evangheliilor" \
    -b "Tâlcuirea Evangheliilor" \
    -e ${DATA_DIR}/trifa_talcuirea_evangheliilor/trifa_talcuirea_evangheliilor.json

echo "Post-processing Trifa - Tâlcuirea Evangheliilor..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_talcuirea_evangheliilor/trifa_talcuirea_evangheliilor.json $@

echo "Removing existing Trifa - Tâlcuirea Evangheliilor using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Tâlcuirea Evangheliilor" $@

echo "Uploading Trifa - Tâlcuirea Evangheliilor..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_talcuirea_evangheliilor/trifa_talcuirea_evangheliilor_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded