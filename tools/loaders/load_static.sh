#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`

DATA_DIR=${CWD}/../../data
IMG_DIR=${CWD}/../../img
TOOLS_DIR=${CWD}/../

${TOOLS_DIR}/od-static-upload.py --input-dir ${DATA_DIR}/uploaded --dest-dir od/data/
${TOOLS_DIR}/od-static-upload.py --input-dir ${IMG_DIR} --dest-dir od/img/