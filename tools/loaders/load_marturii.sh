#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2020-08-05"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Hristos - Marturia mea..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/marturii/marturii.htm -c ${CFG_DIR}/marturii.yaml

echo "Extracting Hristos - Marturia mea..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/marturii/marturii_fixed.htm -c ${CFG_DIR}/marturii.yaml -a "Traian Dorz" -v "Hristos - Marturia mea" -b "Hristos - Marturia mea" -e ${DATA_DIR}/marturii/marturii.json

echo "Post-processing Hristos - Marturia mea..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/marturii/marturii.json

echo "Removing existing Hristos - Marturia mea using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Hristos - Marturia mea" $@

echo "Uploading Hristos - Marturia mea using '$@' flags..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/marturii/marturii_processed.json $@ --date-added ${DATE_ADDED}