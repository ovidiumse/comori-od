#!/bin/sh

DEST="/mnt/c/#work/data"
mkdir -p $DEST

CWD=`realpath $(dirname $0)`

copy() {
    source=$1
    dest=$2

    echo "Copying $source/*.txt to $dest"
    for file in $source/*.txt; do
        cp $file $dest
    done

    echo "Copying $source/*.json  to $dest"
    for file in $source/*.json; do
        cp $file $dest
    done
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

    echo "Checking out $dir/*.txt from HEAD..."
    for file in $dir/*.txt; do
        git restore $(basename $file)
    done
    
    echo "Checking out $dir/*.json from HEAD..."
    for file in $dir/*.json; do
        git restore $(basename $file)
    done

    cd $old_dir

    copy $dir $dest_old
    copy $dest_new $dir
}

prepare_dir "cugetari_total"
prepare_dir "istorii"
prepare_dir "marturii"
prepare_dir "ioan"
prepare_dir "cantari"
prepare_dir "hristos_puterea"
prepare_dir "trifa_talcuiri_culese"
prepare_dir "trifa_spre_canaan"
# prepare_dir "trifa_30_carti"
prepare_dir "test_results"
