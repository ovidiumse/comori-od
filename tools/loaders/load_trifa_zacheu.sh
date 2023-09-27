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

echo "Fixing Trifa - Zacheu..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_zacheu/trifa_zacheu.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Zacheu..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_zacheu/trifa_zacheu.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Zacheu" \
    -b "Zacheu" \
    -e ${DATA_DIR}/trifa_zacheu/trifa_zacheu.json

echo "Post-processing Trifa - Zacheu..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_zacheu/trifa_zacheu.json $@

echo "Removing existing Trifa - Zacheu using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Zacheu" $@

echo "Uploading Trifa - Zacheu..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_zacheu/trifa_zacheu_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded