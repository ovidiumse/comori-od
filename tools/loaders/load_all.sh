#!/bin/bash

CWD=`realpath $(dirname $0)`

DATA_DIR=${CWD}/../../data
MAIN_DIR=${CWD}/../../web/comori-od-all
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


if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Preparing local APIs..."
cd ${MAIN_DIR}
make -f Makefile.local bible-up
cd ${CWD}

# Metadata
${CWD}/load_metadata.sh ${ARGS}

# Preparing uploaded folder
mkdir -p ${DATA_DIR}/uploaded
rm -f "${DATA_DIR}/uploaded/*"

${TOOLS_DIR}/od-upload.py -c ${ARGS}

# Cugetari Nemuritoare
${CWD}/load_cugetari_total.sh ${ARGS}

# Istoria unei Jertfe
${CWD}/load_istorii.sh ${ARGS}

# Hristos - Marturia mea
${CWD}/load_marturii.sh ${ARGS}

# Meditatii la Evanghelia dupa Ioan
${CWD}/load_ioan.sh ${ARGS}

# Cantari Nemuritoare
${CWD}/load_cantari.sh ${ARGS}

# Hristos - Puterea Apostoliei
${CWD}/load_hristos_puterea.sh ${ARGS}

# Spre Canaan
${CWD}/load_trifa_spre_canaan.sh ${ARGS}

# Talcuiri culese din ziare
${CWD}/load_trifa_talcuiri_culese.sh ${ARGS}

# Ce este Oastea Domnului
${CWD}/load_trifa_ce_este_oastea_domnului.sh ${ARGS}

# Strangeti faramiturile
${CWD}/load_strangeti_faramiturile.sh ${ARGS}

${CWD}/load_static.sh ${ARGS}

echo "Restarting comori-od-restapi on ${DOCKER_HOST} to clear caches..."
DOCKER_HOST=${DOCKER_HOST} docker restart comori-od-restapi
echo "Waiting 10 seconds for the service to wake up..."
sleep 10

${CWD}/../test_all.sh ${ARGS}
${CWD}/../prepare_diff.sh
