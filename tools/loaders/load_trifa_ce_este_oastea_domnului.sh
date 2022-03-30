#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2022-03-28"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Trifa - Ce este Oastea Domnului..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/trifa_ce_este_oastea_domnului/trifa_ce_este_oastea_domnului.htm -c ${CFG_DIR}/trifa_ce_este_oastea_domnului.yaml

echo "Extracting Trifa - Ce este Oastea Domnului..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/trifa_ce_este_oastea_domnului/trifa_ce_este_oastea_domnului_fixed.htm \
    -c ${CFG_DIR}/trifa_ce_este_oastea_domnului.yaml \
    -a "Pr. Iosif Trifa" \
    -v "Ce este Oastea Domnului" \
    -b "Ce este Oastea Domnului" \
    -e ${DATA_DIR}/trifa_ce_este_oastea_domnului/trifa_ce_este_oastea_domnului.json

echo "Post-processing Trifa - Ce este Oastea Domnului..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/trifa_ce_este_oastea_domnului/trifa_ce_este_oastea_domnului.json

echo "Removing existing Trifa - Ce este Oastea Domnului using '$@' flags..."
${TOOLS_DIR}/od-remove.py --book "Ce este Oastea Domnului" $@

echo "Uploading Trifa - Ce este Oastea Domnului..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/trifa_ce_este_oastea_domnului/trifa_ce_este_oastea_domnului_processed.json \
    $@ \
    --date-added ${DATE_ADDED} \
    --output-dir ${DATA_DIR}/uploaded