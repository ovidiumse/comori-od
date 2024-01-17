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

echo "Fixing Trifa - La Învierea Domnului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_la_invierea_domnului/trifa_la_invierea_domnului.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - La Învierea Domnului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_la_invierea_domnului/trifa_la_invierea_domnului.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "La Învierea Domnului" \
    -b "La Învierea Domnului" \
    -e ${DATA_DIR}/trifa_la_invierea_domnului/trifa_la_invierea_domnului.json

echo "Post-processing Trifa - La Învierea Domnului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_la_invierea_domnului/trifa_la_invierea_domnului.json $@

echo "Removing existing Trifa - La Învierea Domnului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "La Învierea Domnului" $@

echo "Uploading Trifa - La Învierea Domnului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_la_invierea_domnului/trifa_la_invierea_domnului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded