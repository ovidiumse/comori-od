#!/bin/bash

CWD=`realpath $(dirname $0)`
METADATA_DIR=${CWD}/../../metadata

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

# Upload metadata 
COMORI_OD_API_HOST=${COMORI_OD_API_HOST} ${CWD}/../od-metadata-uploader.py -i ${METADATA_DIR}/authors.yml --endpoint authors $@