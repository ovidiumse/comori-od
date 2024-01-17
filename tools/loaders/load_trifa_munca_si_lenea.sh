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

echo "Fixing Trifa - Munca și lenea..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_munca_si_lenea/trifa_munca_si_lenea.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Munca și lenea..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_munca_si_lenea/trifa_munca_si_lenea.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Munca și lenea" \
    -b "Munca și lenea" \
    -e ${DATA_DIR}/trifa_munca_si_lenea/trifa_munca_si_lenea.json

echo "Post-processing Trifa - Munca și lenea..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_munca_si_lenea/trifa_munca_si_lenea.json $@

echo "Removing existing Trifa - Munca și lenea using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Munca și lenea" $@

echo "Uploading Trifa - Munca și lenea..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_munca_si_lenea/trifa_munca_si_lenea_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded