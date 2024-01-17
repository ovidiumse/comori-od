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

echo "Fixing Trifa - Ca o oaie fără glas..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_ca_o_oaie_fara_glas/trifa_ca_o_oaie_fara_glas.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Ca o oaie fără glas..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_ca_o_oaie_fara_glas/trifa_ca_o_oaie_fara_glas.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Ca o oaie fără glas" \
    -b "Ca o oaie fără glas" \
    -e ${DATA_DIR}/trifa_ca_o_oaie_fara_glas/trifa_ca_o_oaie_fara_glas.json

echo "Post-processing Trifa - Ca o oaie fără glas..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_ca_o_oaie_fara_glas/trifa_ca_o_oaie_fara_glas.json $@

echo "Removing existing Trifa - Ca o oaie fără glas using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Ca o oaie fără glas" $@

echo "Uploading Trifa - Ca o oaie fără glas..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_ca_o_oaie_fara_glas/trifa_ca_o_oaie_fara_glas_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded