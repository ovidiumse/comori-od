#!/bin/bash

CWD=`realpath $(dirname $0)`

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

# Metadata
${CWD}/load_metadata.sh $@
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

${CWD}/../test_all.sh $@
${CWD}/../prepare_diff.sh