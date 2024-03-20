#!/bin/bash

# terminate script if any command failed
set -e

CWD=`realpath $(dirname $0)`

DATA_DIR=${CWD}/../../data
MAIN_DIR=${CWD}/../../web/comori-od-all
IMG_DIR=${CWD}/../../img
TOOLS_DIR=${CWD}/../

ARGS=$@

if [[ -z "${API_TOTP_KEY}" ]]; then
    read -sp "Please enter API_TOTP_KEY: " API_TOTP_KEY
    export API_TOTP_KEY=${API_TOTP_KEY}
fi

echo "Preparing local APIs..."
cd ${MAIN_DIR}
DOCKER_HOST= make -f Makefile.local bible-up
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

# 600 de istorioare
${CWD}/load_trifa_600_istorioare.sh ${ARGS}

# Citiri si talcuiri din Biblie
${CWD}/load_trifa_citiri_si_talcuiri_din_biblie.sh ${ARGS}

# Traim vremuri biblice
${CWD}/load_trifa_traim_vremuri_biblice.sh ${ARGS}

# Oglinda inimii omului
${CWD}/load_trifa_oglinda_inimii_omului.sh ${ARGS}

# Duhul Sfant
${CWD}/load_trifa_duhul_sfant.sh ${ARGS}

# Corabia lui Noe
${CWD}/load_trifa_corabia_lui_noe.sh ${ARGS}

# Pe urmele Mântuitorului
${CWD}/load_trifa_pe_urmele_mantuitorului.sh ${ARGS}

# Zacheu
${CWD}/load_trifa_zacheu.sh ${ARGS}

# Vântul cel ceresc
${CWD}/load_trifa_vantul_cel_ceresc.sh ${ARGS}

# Povestiri religioase
${CWD}/load_trifa_povestiri_religioase.sh ${ARGS}

# Tâlcuirea Evangheliilor
${CWD}/load_trifa_talcuirea_evangheliilor.sh ${ARGS}

# Munca și lenea
${CWD}/load_trifa_munca_si_lenea.sh ${ARGS}

# Mai lângă Domnul meu
${CWD}/load_trifa_mai_langa_domnul_meu.sh ${ARGS}

# La Învierea Domnului
${CWD}/load_trifa_la_invierea_domnului.sh ${ARGS}

# Ia-ți crucea ta
${CWD}/load_trifa_ia-ti_crucea_ta.sh ${ARGS}

# Fricoșii
${CWD}/load_trifa_fricosii.sh ${ARGS}

# Focul cel Ceresc
${CWD}/load_trifa_focul_cel_ceresc.sh ${ARGS}

# Fiul cel pierdut
${CWD}/load_trifa_fiul_cel_pierdut.sh ${ARGS}

# Examenul lui Iov
${CWD}/load_trifa_examenul_lui_iov.sh ${ARGS}

# Din pildele Mântuitorului
${CWD}/load_trifa_din_pildele_mantuitorului.sh ${ARGS}

# Căutați la păsările cerului
${CWD}/load_trifa_cautati_la_pasarile_cerului.sh ${ARGS}

# Ca o oaie fără glas
${CWD}/load_trifa_ca_o_oaie_fara_glas.sh ${ARGS}

# Biblia - Cartea Vieții
${CWD}/load_trifa_biblia_cartea_vietii.sh ${ARGS}

# Ascultarea
${CWD}/load_trifa_ascultarea.sh ${ARGS}

# Alcoolul - Duhul diavolului
${CWD}/load_trifa_alcoolul_duhul_diavolului.sh ${ARGS}

# Adânciri în Evanghelia Mântuitorului
${CWD}/load_trifa_adanciri_in_evanghelia_mantuitorului.sh ${ARGS}

# Hrană pentru familia creștină
${CWD}/load_ioan_marini_hrana_pentru_familia_crestina.sh ${ARGS}

if [ -n "${NGINX_HOST}" ]; then
  DOCKER_HOST=${NGINX_HOST} ${CWD}/load_static.sh ${ARGS}
fi

echo "Restarting comori-od-restapi on ${DOCKER_HOST} to clear caches..."
DOCKER_HOST=${DOCKER_HOST} docker restart comori-od-restapi
echo "Waiting 10 seconds for the service to wake up..."
sleep 10

if [ "${COMORI_OD_API_HOST}" == "http://comori-od-test:9000" ]; then
  ${CWD}/../test_all.sh ${ARGS}
fi

${CWD}/../prepare_diff.sh
