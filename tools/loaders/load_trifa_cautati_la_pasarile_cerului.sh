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

echo "Fixing Trifa - Căutați la păsările cerului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_cautati_la_pasarile_cerului/trifa_cautati_la_pasarile_cerului.htm -c ${CFG_DIR}/trifa_default.yaml

echo "Extracting Trifa - Căutați la păsările cerului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_cautati_la_pasarile_cerului/trifa_cautati_la_pasarile_cerului.htm \
    -c ${CFG_DIR}/trifa_default.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Căutați la păsările cerului" \
    -b "Căutați la păsările cerului" \
    -e ${DATA_DIR}/trifa_cautati_la_pasarile_cerului/trifa_cautati_la_pasarile_cerului.json

echo "Post-processing Trifa - Căutați la păsările cerului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_cautati_la_pasarile_cerului/trifa_cautati_la_pasarile_cerului.json $@

echo "Removing existing Trifa - Căutați la păsările cerului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Căutați la păsările cerului" $@

echo "Uploading Trifa - Căutați la păsările cerului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_cautati_la_pasarile_cerului/trifa_cautati_la_pasarile_cerului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded