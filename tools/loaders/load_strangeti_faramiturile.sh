#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Extracting Strangeti Faramiturile Vol. 4..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/strangeti_faramiturile/test.htm -c ${CFG_DIR}/strangeti_faramiturile.yaml -a "Traian Dorz" -v "Strângeți Fărâmiturile" -b "Strângeți Fărâmiturile Vol. 4" -e ${DATA_DIR}/strangeti_faramiturile/test.json

echo "Post-processing Strangeti Faramiturile Vol. 4..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/strangeti_faramiturile/test.json

echo "Removing existing Strângeți Fărâmiturile using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Strângeți Fărâmiturile" $@

echo "Uploading Strangeti Faramiturile Vol. 4..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/strangeti_faramiturile/test_processed.json $@