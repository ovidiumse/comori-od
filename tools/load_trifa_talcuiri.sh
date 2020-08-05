#!/bin/sh

echo "Fixing Culegeri din ziarele părintelui Iosif Trifa - Tâlcuirea Evangheliilor..."
./od-fix.py -i ../data/trifa_talcuiri.htm -c ../cfg/trifa_talcuiri.yaml
echo "Extracting Culegeri din ziarele părintelui Iosif Trifa - Tâlcuirea Evangheliilor..."
./od-extract.py -i ../data/trifa_talcuiri_fixed.htm -c ../cfg/trifa_talcuiri.yaml -a "Pr. Iosif Trifa" -v "Culegeri din ziarele părintelui Iosif Trifa" -b "Tâlcuirea Evangheliilor" -e ../data/trifa_talcuiri.json
echo "Post-processing Hristos - Puterea Apostoliei..."
./od_postprocess/od_postprocess.py -i ../data/trifa_talcuiri.json
echo "Uploading Hristos - Puterea Apostoliei..."
./od-upload.py -i ../data/trifa_talcuiri_processed.json --index od "$@"