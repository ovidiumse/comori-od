#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2020-07-02"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Cugetari Nemuritoare..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/cugetari_total/cugetari_total.htm \
    -c ${CFG_DIR}/cugetari_total.yaml

echo "Extracting Cugetari Nemuritoare..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cugetari_total/cugetari_total_fixed.htm \
    -c ${CFG_DIR}/cugetari_total.yaml \
    -a "Traian Dorz" \
    -v "Cugetări Nemuritoare" \
    -e ${DATA_DIR}/cugetari_total/cugetari_total.json

echo "Post-processing Cugetari Nemuritoare..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cugetari_total/cugetari_total.json $@

echo "Removing existing Cugetari Nemuritoare using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Cugetări Nemuritoare" $@

echo "Uploading Cugetari Nemuritoare using '$@' flags..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/cugetari_total/cugetari_total_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded 