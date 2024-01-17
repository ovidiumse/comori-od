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

echo "Fixing Trifa - Povestiri religioase..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_povestiri_religioase/trifa_povestiri_religioase.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Povestiri religioase..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_povestiri_religioase/trifa_povestiri_religioase.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Povestiri religioase" \
    -b "Povestiri religioase" \
    -e ${DATA_DIR}/trifa_povestiri_religioase/trifa_povestiri_religioase.json

echo "Post-processing Trifa - Povestiri religioase..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_povestiri_religioase/trifa_povestiri_religioase.json $@

echo "Removing existing Trifa - Povestiri religioase using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Povestiri religioase" $@

echo "Uploading Trifa - Povestiri religioase..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_povestiri_religioase/trifa_povestiri_religioase_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded