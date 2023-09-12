#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Omilii la Evanghelia dupa Matei..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/omilii_iga/Omilii_la_Matei.htm -c ${CFG_DIR}/omilii.yaml

echo "Extracting Omilii la Evanghelia dupa Matei..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/omilii_iga/Omilii_la_Matei_fixed.htm -c ${CFG_DIR}/omilii.yaml -a "Sf. Ioan Gură de Aur" -v "Omilii" -b "Omilii la Evanghelia după Matei" -e ${DATA_DIR}/omilii_iga/Omilii_la_Matei.json

echo "Post-processing Omilii la Evanghelia dupa Matei..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/omilii_iga/Omilii_la_Matei.json

echo "Removing existing Omilii using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Omilii" $@

echo "Uploading Omilii la Evanghelia dupa Matei..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/omilii_iga/Omilii_la_Matei_processed.json $@