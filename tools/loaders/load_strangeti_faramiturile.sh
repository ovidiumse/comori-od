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

echo "Fixing Strangeti Faramiturile..."
${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml &

${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_2.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml &

${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_3.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml &

${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_4.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml &

${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_5.htm \
    -c ${CFG_DIR}/strangeti_faramiturile_6.yaml &

${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_6.htm \
    -c ${CFG_DIR}/strangeti_faramiturile_6.yaml &

${TOOLS_DIR}/od-fix.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_7.htm \
    -c ${CFG_DIR}/strangeti_faramiturile_6.yaml &

for job in `jobs -p`
do
    wait $job
done

echo "Extracting Strangeti Faramiturile..."
${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 1" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1.json &

${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_2_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 2" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_2.json &

${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_3_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 3" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_3.json &

${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_4_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 4" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_4.json &

${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_5_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile_6.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 5" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_5.json &

${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_6_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile_6.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 6" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_6.json &

${TOOLS_DIR}/od-extract.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_7_fixed.htm \
    -c ${CFG_DIR}/strangeti_faramiturile_6.yaml \
    -v "Strângeți Fărâmiturile" \
    -b "Strângeți Fărâmiturile vol. 7" \
    -e ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_7.json &

for job in `jobs -p`
do
    wait $job
done

echo "Post-processing Strangeti Faramiturile..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1.json $@ &

${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_2.json $@ &

${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_3.json $@ &

${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_4.json $@ &

${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_5.json $@ &

${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_6.json $@ &

${TOOLS_DIR}/od_postprocess/od_postprocess.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_7.json $@ &

for job in `jobs -p`
do
    wait $job
done

echo "Removing existing Strângeți Fărâmiturile using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Strângeți Fărâmiturile" $@

echo "Uploading Strangeti Faramiturile using '$@' flags..."
${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_1_processed.json $@ \
    --date-added "2022-12-22" \
    --output-dir ${DATA_DIR}/uploaded

${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_2_processed.json $@ \
    --date-added "2023-03-06" \
    --output-dir ${DATA_DIR}/uploaded

${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_3_processed.json $@ \
    --date-added "2023-07-31" \
    --output-dir ${DATA_DIR}/uploaded

${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_4_processed.json $@ \
    --date-added "2023-07-31" \
    --output-dir ${DATA_DIR}/uploaded

${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_5_processed.json $@ \
    --date-added "2023-07-31" \
    --output-dir ${DATA_DIR}/uploaded

${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_6_processed.json $@ \
    --date-added "2023-02-19" \
    --output-dir ${DATA_DIR}/uploaded

${TOOLS_DIR}/od-upload.py \
    -i ${DATA_DIR}/strangeti_faramiturile/strangeti_faramiturile_7_processed.json $@ \
    --date-added "2023-02-19" \
    --output-dir ${DATA_DIR}/uploaded