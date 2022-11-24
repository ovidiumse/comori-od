#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg
DATE_ADDED="2020-08-05"

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Extracting Cantari Nemuritoare..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_1.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_1.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_2.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_2.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_3.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_3.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_4.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_4.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_6.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_6.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_7.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_7.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_8.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_8.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_9.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_9.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_10.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_10.json &
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/cantari/cantari_11.htm -c ${CFG_DIR}/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -e ${DATA_DIR}/cantari/cantari_11.json &

wait

echo "Post-processing Cantari Nemuritoare..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_1.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_2.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_3.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_4.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_6.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_7.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_8.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_9.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_10.json $@ &
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/cantari/cantari_11.json $@ &

wait 

echo "Removing existing Cântări Nemuritoare using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Cântări Nemuritoare" $@

echo "Uploading Cantari Nemuritoare using '$@' flags..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_1_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_2_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_3_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_4_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_6_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_7_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_8_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_9_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_10_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/cantari/cantari_11_processed.json $@ --date-added ${DATE_ADDED} --output-dir ${DATA_DIR}/uploaded