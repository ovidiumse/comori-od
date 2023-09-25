#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2023-09-25"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Pe urmele Mântuitorului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_pe_urmele_mantuitorului/trifa_pe_urmele_mantuitorului.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Pe urmele Mântuitorului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_pe_urmele_mantuitorului/trifa_pe_urmele_mantuitorului_fixed.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Pe urmele Mântuitorului" \
    -b "Pe urmele Mântuitorului" \
    -e ${DATA_DIR}/trifa_pe_urmele_mantuitorului/trifa_pe_urmele_mantuitorului.json

echo "Post-processing Trifa - Pe urmele Mântuitorului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_pe_urmele_mantuitorului/trifa_pe_urmele_mantuitorului.json $@

echo "Removing existing Trifa - Pe urmele Mântuitorului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Pe urmele Mântuitorului" $@

echo "Uploading Trifa - Pe urmele Mântuitorului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_pe_urmele_mantuitorului/trifa_pe_urmele_mantuitorului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded