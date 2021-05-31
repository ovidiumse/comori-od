#!/bin/sh

DEST="/mnt/c/#work/data"
mkdir -p $DEST

CWD=`realpath $(dirname $0)`

copy() {
    source=$1
    dest=$2

    for file in $source/*.txt; do
        echo "Copying $file to $dest"
        cp $file $dest
    done

    for file in $source/*.json; do
        echo "Copying $file to $dest"
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

    echo "Checking out $dir/*.txt from HEAD..."
    git checkout $dir/*.txt
    
    echo "Checking out $dir/*.json from HEAD..."
    git checkout $dir/*.json

    copy $dir $dest_old
    copy $dest_new $dir
}

prepare_dir "cugetari_total"
prepare_dir "istorii"
prepare_dir "marturii"
prepare_dir "ioan"
prepare_dir "cantari"
prepare_dir "hristos_puterea"
prepare_dir "trifa_30_carti"
prepare_dir "test_results"
