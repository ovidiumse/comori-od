#!/bin/bash

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/../
DATA_DIR=${CWD}/../../data
CFG_DIR=${CWD}/../../cfg

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Fixing Meditatii la Ev. dupa Ioan..."
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_1.htm -c ${CFG_DIR}/ioan.yaml
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_2.htm -c ${CFG_DIR}/ioan.yaml
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_3.htm -c ${CFG_DIR}/ioan.yaml
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_4.htm -c ${CFG_DIR}/ioan.yaml
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_5.htm -c ${CFG_DIR}/ioan.yaml
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_6.htm -c ${CFG_DIR}/ioan.yaml
${TOOLS_DIR}/od-fix.py -i ${DATA_DIR}/ioan/ioan_7.htm -c ${CFG_DIR}/ioan.yaml

echo "Extracting Meditatii la Ev. dupa Ioan..."
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_1_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_1.json
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_2_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_2.json
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_3_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_3.json
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_4_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_4.json
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_5_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_5.json
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_6_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_6.json
${TOOLS_DIR}/od-extract.py -i ${DATA_DIR}/ioan/ioan_7_fixed.htm -c ${CFG_DIR}/ioan.yaml  -a "Traian Dorz" -v "Meditații la Ev. după Ioan" -e ${DATA_DIR}/ioan/ioan_7.json

echo "Post-processing Meditatii la Ev. dupa Ioan..."
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_1.json
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_2.json
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_3.json
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_4.json
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_5.json
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_6.json
${TOOLS_DIR}/od_postprocess/od_postprocess.py -i ${DATA_DIR}/ioan/ioan_7.json

echo "Removing existing Meditații la Ev. după Ioan using '$@' flags..."
${TOOLS_DIR}/od-remove.py --volume "Meditații la Ev. după Ioan" $@

echo "Uploading Meditatii la Ev. dupa Ioan using '$@' flags..."
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_1_processed.json $@
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_2_processed.json $@
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_3_processed.json $@
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_4_processed.json $@
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_5_processed.json $@
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_6_processed.json $@
${TOOLS_DIR}/od-upload.py -i ${DATA_DIR}/ioan/ioan_7_processed.json $@