#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Talcuirea Evangheliilor..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_talcuiri_culese/trifa_talcuiri_culese.htm -c ${CFG_DIR}/trifa_talcuiri_culese.yaml

echo "Extracting Trifa - Talcuirea Evangheliilor..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/trifa_talcuiri_culese/trifa_talcuiri_culese_fixed.htm -c ${CFG_DIR}/trifa_talcuiri_culese.yaml -a "Pr. Iosif Trifa" -v "Culese din ziare" -b "Tâlcuiri culese din ziare" -e ${DATA_DIR}/trifa_talcuiri_culese/trifa_talcuiri_culese.json

echo "Post-processing Trifa - Talcuirea Evangheliilor..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_talcuiri_culese/trifa_talcuiri_culese.json

echo "Removing existing Trifa - Talcuirea Evangheliilor using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Talcuirea Evangheliilor" $@

echo "Uploading Trifa - Talcuirea Evangheliilor..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/trifa_talcuiri_culese/trifa_talcuiri_culese_processed.json $@