#!/bin/sh

host_type=${1:-}

echo "Extracting Istoria unei Jertfe..."
./od-extract.py -i ../data/istorii_1.htm -c ../cfg/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 1, Grăuntele (1923 - 1935)" -e ../data/istorii_1.json
./od-extract.py -i ../data/istorii_2.htm -c ../cfg/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 2, Cernerea (1935 - 1947)" -e ../data/istorii_2.json
./od-extract.py -i ../data/istorii_3.htm -c ../cfg/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 3, Rugul (1947 - 1977)" -e ../data/istorii_3.json
./od-extract.py -i ../data/istorii_4.htm -c ../cfg/istorii.yaml -a "Traian Dorz" -v "Istoria unei Jertfe" -b "Istoria unei Jertfe vol. 4, Pârga (1977 - 1989)" -e ../data/istorii_4.json
echo "Post-processing Istoria unei Jertfe..."
./od_postprocess/od_postprocess.py -i ../data/istorii_1.json
./od_postprocess/od_postprocess.py -i ../data/istorii_2.json
./od_postprocess/od_postprocess.py -i ../data/istorii_3.json
./od_postprocess/od_postprocess.py -i ../data/istorii_4.json
echo "Uploading Istoria unei Jertfe using $host_type flag..."
./od-upload.py -i ../data/istorii_1_processed.json --index od $host_type
./od-upload.py -i ../data/istorii_2_processed.json --index od $host_type
./od-upload.py -i ../data/istorii_3_processed.json --index od $host_type
./od-upload.py -i ../data/istorii_4_processed.json --index od $host_type