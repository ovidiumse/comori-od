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

echo "Fixing Trifa - Ia-ți crucea ta..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_ia-ti_crucea_ta/trifa_ia-ti_crucea_ta.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Ia-ți crucea ta..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_ia-ti_crucea_ta/trifa_ia-ti_crucea_ta.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Ia-ți crucea ta" \
    -b "Ia-ți crucea ta" \
    -e ${DATA_DIR}/trifa_ia-ti_crucea_ta/trifa_ia-ti_crucea_ta.json

echo "Post-processing Trifa - Ia-ți crucea ta..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_ia-ti_crucea_ta/trifa_ia-ti_crucea_ta.json $@

echo "Removing existing Trifa - Ia-ți crucea ta using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Ia-ți crucea ta" $@

echo "Uploading Trifa - Ia-ți crucea ta..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_ia-ti_crucea_ta/trifa_ia-ti_crucea_ta_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded