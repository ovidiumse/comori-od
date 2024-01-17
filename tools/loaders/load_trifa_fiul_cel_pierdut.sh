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

echo "Fixing Trifa - Fiul cel pierdut..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_fiul_cel_pierdut/trifa_fiul_cel_pierdut.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Fiul cel pierdut..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_fiul_cel_pierdut/trifa_fiul_cel_pierdut.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Fiul cel pierdut" \
    -b "Fiul cel pierdut" \
    -e ${DATA_DIR}/trifa_fiul_cel_pierdut/trifa_fiul_cel_pierdut.json

echo "Post-processing Trifa - Fiul cel pierdut..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_fiul_cel_pierdut/trifa_fiul_cel_pierdut.json $@

echo "Removing existing Trifa - Fiul cel pierdut using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Fiul cel pierdut" $@

echo "Uploading Trifa - Fiul cel pierdut..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_fiul_cel_pierdut/trifa_fiul_cel_pierdut_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded