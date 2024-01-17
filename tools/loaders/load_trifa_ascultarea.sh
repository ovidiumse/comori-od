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

echo "Fixing Trifa - Ascultarea..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_ascultarea/trifa_ascultarea.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Ascultarea..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_ascultarea/trifa_ascultarea.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Ascultarea" \
    -b "Ascultarea" \
    -e ${DATA_DIR}/trifa_ascultarea/trifa_ascultarea.json

echo "Post-processing Trifa - Ascultarea..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_ascultarea/trifa_ascultarea.json $@

echo "Removing existing Trifa - Ascultarea using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Ascultarea" $@

echo "Uploading Trifa - Ascultarea..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_ascultarea/trifa_ascultarea_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded