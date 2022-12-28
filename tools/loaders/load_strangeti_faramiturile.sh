#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2022-12-22"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Strangeti Faramiturile..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1.htm -c ${CFG_DIR}/strangeti_faramiturile.yaml &

wait

echo "Extracting Strangeti Faramiturile..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1_fixed.htm -c ${CFG_DIR}/strangeti_faramiturile.yaml -v "Strângeți Fărâmiturile" -b "Strângeți Fărâmiturile vol. 1" -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1.json &

wait

echo "Post-processing Strangeti Faramiturile..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1.json $@ &

wait

echo "Removing existing Strângeți Fărâmiturile using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Strângeți Fărâmiturile" $@

echo "Uploading Strangeti Faramiturile using '$@' flags..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded