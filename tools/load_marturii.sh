#!/bin/sh

host_type=${1:-}

echo "Extracting Hristos - Marturia mea..."
./od-extract.py -i ../data/marturii.htm -c ../cfg/marturii.yaml -a "Traian Dorz" -v "Hristos - Marturia mea" -b "Hristos - Marturia mea" -e ../data/marturii.json
echo "Post-processing Hristos - Marturia mea..."
./od_postprocess/od_postprocess.py -i ../data/marturii.json
echo "Uploading Hristos - Marturia mea using $host_type flag..."
./od-upload.py -i ../data/marturii_processed.json --index od $host_type