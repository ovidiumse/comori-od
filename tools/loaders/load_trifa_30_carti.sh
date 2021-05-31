#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - 30 carti..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_30_carti/trifa_30_carti.htm -c ${CFG_DIR}/trifa_30_carti.yaml

echo "Extracting Trifa - 30 carti..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/trifa_30_carti/trifa_30_carti_fixed.htm -c ${CFG_DIR}/trifa_30_carti.yaml -a "Pr. Iosif Trifa" -v "30 de cărti" -e ${DATA_DIR}/trifa_30_carti/trifa_30_carti.json

echo "Post-processing Trifa - 30 carti..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_30_carti/trifa_30_carti.json

echo "Removing existing Trifa - 30 carti using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "30 de cărti" $@

echo "Uploading Trifa - 30 de carti..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/trifa_30_carti/trifa_30_carti_processed.json $@