#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`
TOOLS_DIR=${CWD}/..
DATA_DIR=${CWD}/../../data

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Post-processing Bible..."
${TOOLS_DIR}/bible-postprocess.py \
    --input-file ${DATA_DIR}/bible/bible.json \
    --output-file ${DATA_DIR}/bible/bible-postprocessed.json \
    --bible-api ${BIBLE_API} \
    --bible-aliases-file ${DATA_DIR}/bible/bible-aliases.json \
    --bible-root-names-file ${DATA_DIR}/bible/bible-root-names.json \
    --bible-reverse-refs-file ${DATA_DIR}/bible/bible-reverse-refs.json \
    --bible-refs-file ${DATA_DIR}/bible/bible-refs.json

echo "Deleting and recreating Bible index..."
${TOOLS_DIR}/bible-upload.py -d -c

echo "Uploading Bible..."
${TOOLS_DIR}/bible-upload.py --input ${DATA_DIR}/bible/bible-postprocessed.json