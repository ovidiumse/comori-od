#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2020-08-05"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Istoria unei Jertfe..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/istorii/istorii_1.htm -c ${CFG_DIR}/istorii.yaml &
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/istorii/istorii_2.htm -c ${CFG_DIR}/istorii.yaml &
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/istorii/istorii_3.htm -c ${CFG_DIR}/istorii.yaml &
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/istorii/istorii_4.htm -c ${CFG_DIR}/istorii.yaml &

for job in `jobs -p`
do
    wait $job
done

echo "Extracting Istoria unei Jertfe..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/istorii/istorii_1_fixed.htm -c ${CFG_DIR}/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 1" -fb "Istoria unei Jertfe vol. 1, Grăuntele (1923 - 1935)" -e ${DATA_DIR}/istorii/istorii_1.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/istorii/istorii_2_fixed.htm -c ${CFG_DIR}/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 2" -fb "Istoria unei Jertfe vol. 2, Cernerea (1935 - 1947)" -e ${DATA_DIR}/istorii/istorii_2.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/istorii/istorii_3_fixed.htm -c ${CFG_DIR}/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 3" -fb "Istoria unei Jertfe vol. 3, Rugul (1947 - 1977)" -e ${DATA_DIR}/istorii/istorii_3.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/istorii/istorii_4_fixed.htm -c ${CFG_DIR}/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 4" -fb "Istoria unei Jertfe vol. 4, Pârga (1977 - 1989)" -e ${DATA_DIR}/istorii/istorii_4.json &

for job in `jobs -p`
do
    wait $job
done

echo "Post-processing Istoria unei Jertfe..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/istorii/istorii_1.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/istorii/istorii_2.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/istorii/istorii_3.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/istorii/istorii_4.json $@ &

for job in `jobs -p`
do
    wait $job
done

echo "Removing existing Istoria unei Jertfe using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Istoria unei Jertfe" $@

echo "Uploading Istoria unei Jertfe using '$@' flags..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/istorii/istorii_1_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/istorii/istorii_2_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/istorii/istorii_3_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/istorii/istorii_4_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded