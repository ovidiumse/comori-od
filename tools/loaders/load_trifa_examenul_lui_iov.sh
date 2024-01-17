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

echo "Fixing Trifa - Examenul lui Iov..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_examenul_lui_iov/trifa_examenul_lui_iov.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Examenul lui Iov..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_examenul_lui_iov/trifa_examenul_lui_iov.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Examenul lui Iov" \
    -b "Examenul lui Iov" \
    -e ${DATA_DIR}/trifa_examenul_lui_iov/trifa_examenul_lui_iov.json

echo "Post-processing Trifa - Examenul lui Iov..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_examenul_lui_iov/trifa_examenul_lui_iov.json $@

echo "Removing existing Trifa - Examenul lui Iov using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Examenul lui Iov" $@

echo "Uploading Trifa - Examenul lui Iov..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_examenul_lui_iov/trifa_examenul_lui_iov_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded