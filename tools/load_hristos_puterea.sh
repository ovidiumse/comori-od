#!/bin/sh

echo "Fixing Hristos - Puterea Apostoliei..."
./od-fix.py -i ../data/hristos_puterea/hristos_puterea.htm -c ../cfg/hristos_puterea.yaml

echo "Extracting Hristos - Puterea Apostoliei..."
./od-extract.py -i ../data/hristos_puterea/hristos_puterea_fixed.htm -c ../cfg/hristos_puterea.yaml -a "Traian Dorz" -v "Hristos - Puterea Apostoliei" -b "Hristos - Puterea Apostoliei" -e ../data/hristos_puterea/hristos_puterea.json

echo "Post-processing Hristos - Puterea Apostoliei..."
./od_postprocess/od_postprocess.py -i ../data/hristos_puterea/hristos_puterea.json

echo "Uploading Hristos - Puterea Apostoliei using '$@'' flags..."
./od-upload.py -i ../data/hristos_puterea/hristos_puterea_processed.json --index od $@