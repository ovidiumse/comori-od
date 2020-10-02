#!/bin/sh

echo "Fixing Cugetari Nemuritoare..."
./od-fix.py -i ../data/cugetari_total/cugetari_total.htm -c ../cfg/cugetari_total.yaml

echo "Extracting Cugetari Nemuritoare..."
./od-extract.py -i ../data/cugetari_total/cugetari_total_fixed.htm -c ../cfg/cugetari_total.yaml -a "Traian Dorz" -e ../data/cugetari_total/cugetari_total.json

echo "Post-processing Cugetari Nemuritoare..."
./od_postprocess/od_postprocess.py -i ../data/cugetari_total/cugetari_total.json

echo "Uploading Cugetari Nemuritoare using '$@' flags..."
./od-upload.py -i ../data/cugetari_total/cugetari_total_processed.json --index od $@