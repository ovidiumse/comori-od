#!/bin/sh

host_type=${1:-}

echo "Extracting Cantari Nemuritoare..."
./od-extract.py -i ../data/cantari_1.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 1" -e ../data/cantari_1.json
./od-extract.py -i ../data/cantari_2.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 2" -e ../data/cantari_2.json
./od-extract.py -i ../data/cantari_3.htm -c ../cfg/cantari_3.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 3" -e ../data/cantari_3.json
./od-extract.py -i ../data/cantari_4.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 4" -e ../data/cantari_4.json
./od-extract.py -i ../data/cantari_6.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 6" -e ../data/cantari_6.json
./od-extract.py -i ../data/cantari_7.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 7" -e ../data/cantari_7.json
./od-extract.py -i ../data/cantari_8.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 8" -e ../data/cantari_8.json
./od-extract.py -i ../data/cantari_9.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 9" -e ../data/cantari_9.json
./od-extract.py -i ../data/cantari_10.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 10" -e ../data/cantari_10.json
./od-extract.py -i ../data/cantari_11.htm -c ../cfg/cantari.yaml -a "Traian Dorz" -v "Cântări Nemuritoare" -b "Cântări Nemuritoare vol. 11" -e ../data/cantari_11.json
echo "Post-processing Cantari Nemuritoare..."
./od_postprocess/od_postprocess.py -i ../data/cantari_1.json
./od_postprocess/od_postprocess.py -i ../data/cantari_2.json
./od_postprocess/od_postprocess.py -i ../data/cantari_3.json
./od_postprocess/od_postprocess.py -i ../data/cantari_4.json
./od_postprocess/od_postprocess.py -i ../data/cantari_6.json
./od_postprocess/od_postprocess.py -i ../data/cantari_7.json
./od_postprocess/od_postprocess.py -i ../data/cantari_8.json
./od_postprocess/od_postprocess.py -i ../data/cantari_9.json
./od_postprocess/od_postprocess.py -i ../data/cantari_10.json
./od_postprocess/od_postprocess.py -i ../data/cantari_11.json
echo "Uploading Cantari Nemuritoare using $host_type flag..."
./od-upload.py -i ../data/cantari_1_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_2_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_3_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_4_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_6_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_7_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_8_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_9_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_10_processed.json --index od $host_type
./od-upload.py -i ../data/cantari_11_processed.json --index od $host_type