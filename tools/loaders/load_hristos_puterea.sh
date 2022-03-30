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

echo "Fixing Hristos - Puterea Apostoliei..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/hristos_puterea/hristos_puterea.htm -c ${CFG_DIR}/hristos_puterea.yaml

echo "Extracting Hristos - Puterea Apostoliei..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/hristos_puterea/hristos_puterea_fixed.htm -c ${CFG_DIR}/hristos_puterea.yaml -a "Traian Dorz" -v "Hristos - Puterea Apostoliei" -b "Hristos - Puterea Apostoliei" -e ${DATA_DIR}/hristos_puterea/hristos_puterea.json

echo "Post-processing Hristos - Puterea Apostoliei..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/hristos_puterea/hristos_puterea.json

echo "Removing existing Hristos - Puterea Apostoliei using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Hristos - Puterea Apostoliei" $@

echo "Uploading Hristos - Puterea Apostoliei using '$@'' flags..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/hristos_puterea/hristos_puterea_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded