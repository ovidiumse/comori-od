#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2024-01-12"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Marini - Hrană pentru familia creștină..."
${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/ioan_marini_hrana_pentru_familia_crestina/ioan_marini_hrana_pentru_familia_crestina.htm \
    -c ${CFG_DIR}/ioan_marini_hrana_pentru_familia_crestina.yaml

echo "Extracting Marini - Hrană pentru familia creștină..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/ioan_marini_hrana_pentru_familia_crestina/ioan_marini_hrana_pentru_familia_crestina_fixed.htm \
    -c ${CFG_DIR}/ioan_marini_hrana_pentru_familia_crestina.yaml \
    -a "Ioan Marini" \
    -v "Hrană pentru familia creștină" \
    -b "Hrană pentru familia creștină" \
    -e ${DATA_DIR}/ioan_marini_hrana_pentru_familia_crestina/ioan_marini_hrana_pentru_familia_crestina.json

echo "Post-processing Marini - Hrană pentru familia creștină..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan_marini_hrana_pentru_familia_crestina/ioan_marini_hrana_pentru_familia_crestina.json $@

echo "Removing existing Marini - Hrană pentru familia creștină using '$@' flags..."
${TOOLS_DIR}/od-remove.py --book "Hrană pentru familia creștină" $@

echo "Uploading Marini - Hrană pentru familia creștină..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/ioan_marini_hrana_pentru_familia_crestina/ioan_marini_hrana_pentru_familia_crestina_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded