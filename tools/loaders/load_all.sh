#!/bin/bash

CWD=`realpath $(dirname $0)`

DATA_DIR=${CWD}/../../data
TOOLS_DIR=${CWD}/../
NGINX_DATA_DIR=${CWD}/../../web/comori-od-nginx-proxy/data

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

# Metadata
${CWD}/load_metadata.sh $@

rm -f ${DATA_DIR}/uploaded/*

# Cugetari Nemuritoare
${CWD}/load_cugetari_total.sh $@

# Istoria unei Jertfe
${CWD}/load_istorii.sh $@

# Hristos - Marturia mea
${CWD}/load_marturii.sh $@

# Meditatii la Evanghelia dupa Ioan
${CWD}/load_ioan.sh $@

# Cantari Nemuritoare
${CWD}/load_cantari.sh $@

# Hristos - Puterea Apostoliei
${CWD}/load_hristos_puterea.sh $@

# Spre Canaan
${CWD}/load_trifa_spre_canaan.sh $@

# Talcuiri culese din ziare
${CWD}/load_trifa_talcuiri_culese.sh $@

# Ce este Oastea Domnului
${CWD}/load_trifa_ce_este_oastea_domnului.sh $@

${CWD}/../test_all.sh $@
${CWD}/../prepare_diff.sh

${TOOLS_DIR}/od-static-upload.py --input-dir ${DATA_DIR}/uploaded $@