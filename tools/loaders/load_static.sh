#!/bin/bash

CWD=`realpath $(dirname $0)`

DATA_DIR=${CWD}/../../data
IMG_DIR=${CWD}/../../img
TOOLS_DIR=${CWD}/../

ARGS=$@

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--index)
      IDX_NAME="$2"
      ARGS+=("$1", "$2")
      shift # past argument
      shift # past value
      ;;
    *)
      ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

${TOOLS_DIR}/od-static-upload.py --input-dir ${DATA_DIR}/uploaded --dest-dir ${IDX_NAME}/data/ ${ARGS}
${TOOLS_DIR}/od-static-upload.py --input-dir ${IMG_DIR} --dest-dir ${IDX_NAME}/img/ ${ARGS}