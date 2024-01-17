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

echo "Fixing Trifa - Alcoolul - Duhul diavolului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_alcoolul_duhul_diavolului/trifa_alcoolul_duhul_diavolului.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Alcoolul - Duhul diavolului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_alcoolul_duhul_diavolului/trifa_alcoolul_duhul_diavolului.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Alcoolul - Duhul diavolului" \
    -b "Alcoolul - Duhul diavolului" \
    -e ${DATA_DIR}/trifa_alcoolul_duhul_diavolului/trifa_alcoolul_duhul_diavolului.json

echo "Post-processing Trifa - Alcoolul - Duhul diavolului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_alcoolul_duhul_diavolului/trifa_alcoolul_duhul_diavolului.json $@

echo "Removing existing Trifa - Alcoolul - Duhul diavolului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Alcoolul - Duhul diavolului" $@

echo "Uploading Trifa - Alcoolul - Duhul diavolului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_alcoolul_duhul_diavolului/trifa_alcoolul_duhul_diavolului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded