#!/usr/bin/sh

CWD=`realpath $(dirname $0)`

SRC_DIR=/mnt/backup/comori-od/books/
DATA_DIR=${CWD}/../data

cp ${SRC_DIR}/cugetari_total.* ${DATA_DIR}/cugetari_total/
cp ${SRC_DIR}/istorii_?.* ${DATA_DIR}/istorii/
cp ${SRC_DIR}/marturii.* ${DATA_DIR}/marturii/
cp ${SRC_DIR}/ioan_?.* ${DATA_DIR}/ioan/
cp ${SRC_DIR}/cantari_*.* ${DATA_DIR}/cantari/
cp ${SRC_DIR}/hristos_puterea.* ${DATA_DIR}/hristos_puterea/
cp ${SRC_DIR}/trifa_spre_canaan.* ${DATA_DIR}/trifa_spre_canaan/
cp ${SRC_DIR}/trifa_talcuiri_culese.* ${DATA_DIR}/trifa_talcuiri_culese/
cp ${SRC_DIR}/trifa_ce_este_oastea_domnului.* ${DATA_DIR}/trifa_ce_este_oastea_domnului/
cp ${SRC_DIR}/strangeti_faramiturile_?.* ${DATA_DIR}/strangeti_faramiturile/
cp ${SRC_DIR}/trifa_600_istorioare.* ${DATA_DIR}/trifa_600_istorioare/
cp ${SRC_DIR}/trifa_citiri_si_talcuiri_din_biblie.* ${DATA_DIR}/trifa_citiri_si_talcuiri_din_biblie/