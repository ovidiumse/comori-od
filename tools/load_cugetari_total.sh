#!/bin/sh

host_type=${1:-}

echo "Extracting Cugetari Nemuritoare..."
./od-extract.py -i ../data/cugetari_total.htm -c ../cfg/cugetari_total.yaml -a "Traian Dorz" -e ../data/cugetari_total.json
echo "Post-processing Cugetari Nemuritoare..."
./od_postprocess/od_postprocess.py -i ../data/cugetari_total.json
echo "Uploading Cugetari Nemuritoare using $host_type flag..."
./od-upload.py -i ../data/cugetari_total_processed.json --index od $host_type