#!/bin/bash

CWD=`realpath $(dirname $0)`

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

# Cugetari Nemuritoare
${CWD}/load_cugetari_total.sh $@ &

# Istoria unei Jertfe
${CWD}/load_istorii.sh $@ &

wait

# Hristos - Marturia mea
${CWD}/load_marturii.sh $@ &

# Meditatii la Evanghelia dupa Ioan
${CWD}/load_ioan.sh $@ &

wait

# Cantari Nemuritoare
${CWD}/load_cantari.sh $@ &

# Hristos - Puterea Apostoliei
${CWD}/load_hristos_puterea.sh $@ &

# Spre Canaan
${CWD}/load_trifa_spre_canaan.sh $@ &
 
# wait for all loaders to complete
wait

${CWD}/../test_all.sh $@
${CWD}/../prepare_diff.sh