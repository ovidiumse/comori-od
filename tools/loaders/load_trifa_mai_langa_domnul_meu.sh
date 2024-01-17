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

echo "Fixing Trifa - Mai lângă Domnul meu..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_mai_langa_domnul_meu/trifa_mai_langa_domnul_meu.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Mai lângă Domnul meu..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_mai_langa_domnul_meu/trifa_mai_langa_domnul_meu.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Mai lângă Domnul meu" \
    -b "Mai lângă Domnul meu" \
    -e ${DATA_DIR}/trifa_mai_langa_domnul_meu/trifa_mai_langa_domnul_meu.json

echo "Post-processing Trifa - Mai lângă Domnul meu..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_mai_langa_domnul_meu/trifa_mai_langa_domnul_meu.json $@

echo "Removing existing Trifa - Mai lângă Domnul meu using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Mai lângă Domnul meu" $@

echo "Uploading Trifa - Mai lângă Domnul meu..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_mai_langa_domnul_meu/trifa_mai_langa_domnul_meu_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded