#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2024-01-16"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Adânciri în Evanghelia Mântuitorului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_adanciri_in_evanghelia_mantuitorului/trifa_adanciri_in_evanghelia_mantuitorului.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Adânciri în Evanghelia Mântuitorului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_adanciri_in_evanghelia_mantuitorului/trifa_adanciri_in_evanghelia_mantuitorului.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Adânciri în Evanghelia Mântuitorului" \
    -b "Adânciri în Evanghelia Mântuitorului" \
    -e ${DATA_DIR}/trifa_adanciri_in_evanghelia_mantuitorului/trifa_adanciri_in_evanghelia_mantuitorului.json

echo "Post-processing Trifa - Adânciri în Evanghelia Mântuitorului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_adanciri_in_evanghelia_mantuitorului/trifa_adanciri_in_evanghelia_mantuitorului.json $@

echo "Removing existing Trifa - Adânciri în Evanghelia Mântuitorului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Adânciri în Evanghelia Mântuitorului" $@

echo "Uploading Trifa - Adânciri în Evanghelia Mântuitorului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_adanciri_in_evanghelia_mantuitorului/trifa_adanciri_in_evanghelia_mantuitorului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded