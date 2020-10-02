#!/bin/sh

echo "Fixing Hristos - Marturia mea..."
./od-fix.py -i ../data/marturii/marturii.htm -c ../cfg/marturii.yaml

echo "Extracting Hristos - Marturia mea..."
./od-extract.py -i ../data/marturii/marturii_fixed.htm -c ../cfg/marturii.yaml -a "Traian Dorz" -v "Hristos - Marturia mea" -b "Hristos - Marturia mea" -e ../data/marturii/marturii.json

echo "Post-processing Hristos - Marturia mea..."
./od_postprocess/od_postprocess.py -i ../data/marturii/marturii.json

echo "Uploading Hristos - Marturia mea using '$@'' flags..."
./od-upload.py -i ../data/marturii/marturii_processed.json --index od $@