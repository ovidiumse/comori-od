#!/bin/sh

DEST="/mnt/backup/comori-od/diffs"
mkdir -p $DEST

CWD=`realpath $(dirname $0)`

copy() {
    source=$1
    dest=$2

    for file in $source/*.txt; do
        cp $file $dest &
    done

    for file in $source/*.json; do
        cp $file $dest &
    done

    wait
}

prepare_dir() {
    dir=$CWD/../data/$1
    dest_old=$DEST/old/$1/
    dest_new=$DEST/new/$1/

    mkdir -p $dest_old
    mkdir -p $dest_new

    copy $dir $dest_new

    old_dir=$CWD
    cd $dir

    echo "Checking out $dir..."

    for file in $dir/*.txt; do
        git restore $(basename $file)
    done

    for file in $dir/*.json; do
        git restore $(basename $file)
    done

    cd $old_dir

    echo "Copying $dir to $dest_old..."
    copy $dir $dest_old

    echo "Copying $dest_new to $dir..."
    copy $dest_new $dir

    echo "Replacing links for $dir..."
    for file in $dest_old/*.json; do
        sed -i 's/testapi.comori-od.ro/api.comori-od.ro/g' $file
        sed -i 's/localhost:9000/api.comori-od.ro/g' $file
    done

    for file in $dest_new/*.json; do
        sed -i 's/testapi.comori-od.ro/api.comori-od.ro/g' $file
        sed -i 's/localhost:9000/api.comori-od.ro/g' $file
    done

    wait
}

prepare_dir "cugetari_total"
prepare_dir "istorii"
prepare_dir "marturii"
prepare_dir "ioan"
prepare_dir "cantari"
prepare_dir "hristos_puterea"
prepare_dir "trifa_spre_canaan"
prepare_dir "trifa_talcuiri_culese"
prepare_dir "trifa_ce_este_oastea_domnului"
prepare_dir "strangeti_faramiturile"
prepare_dir "trifa_600_istorioare"
prepare_dir "trifa_citiri_si_talcuiri_din_biblie"
prepare_dir "trifa_traim_vremuri_biblice"
prepare_dir "trifa_oglinda_inimii_omului"
prepare_dir "trifa_duhul_sfant"
prepare_dir "trifa_corabia_lui_noe"
prepare_dir "trifa_pe_urmele_mantuitorului"
prepare_dir "trifa_zacheu"
prepare_dir "ioan_marini_hrana_pentru_familia_crestina"
prepare_dir "test_results"
