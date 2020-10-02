#!/bin/sh

echo "Extracting Meditatii la Evanghelia dupa Ioan..."
./od-fix.py -i ../data/ioan/ioan_1.htm -c ../cfg/ioan.yaml
./od-fix.py -i ../data/ioan/ioan_2.htm -c ../cfg/ioan.yaml
./od-fix.py -i ../data/ioan/ioan_3.htm -c ../cfg/ioan.yaml
./od-fix.py -i ../data/ioan/ioan_4.htm -c ../cfg/ioan.yaml
./od-fix.py -i ../data/ioan/ioan_5.htm -c ../cfg/ioan.yaml
./od-fix.py -i ../data/ioan/ioan_6.htm -c ../cfg/ioan.yaml
./od-fix.py -i ../data/ioan/ioan_7.htm -c ../cfg/ioan.yaml

echo "Extracting Meditatii la Evanghelia dupa Ioan..."
./od-extract.py -i ../data/ioan/ioan_1_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 1" -e ../data/ioan/ioan_1.json
./od-extract.py -i ../data/ioan/ioan_2_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 2" -e ../data/ioan/ioan_2.json
./od-extract.py -i ../data/ioan/ioan_3_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 3" -e ../data/ioan/ioan_3.json
./od-extract.py -i ../data/ioan/ioan_4_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 4" -e ../data/ioan/ioan_4.json
./od-extract.py -i ../data/ioan/ioan_5_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 5" -e ../data/ioan/ioan_5.json
./od-extract.py -i ../data/ioan/ioan_6_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 6" -e ../data/ioan/ioan_6.json
./od-extract.py -i ../data/ioan/ioan_7_fixed.htm -c ../cfg/ioan.yaml  -a "Traian Dorz" -v "Meditații la Evanghelia după Ioan" -b "Meditații la Evanghelia după Ioan vol. 7" -e ../data/ioan/ioan_7.json

echo "Post-processing Meditatii la Evanghelia dupa Ioan..."
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_1.json
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_2.json
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_3.json
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_4.json
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_5.json
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_6.json
./od_postprocess/od_postprocess.py -i ../data/ioan/ioan_7.json

echo "Uploading Meditatii la Evanghelia dupa Ioan using '$@' flags..."
./od-upload.py -i ../data/ioan/ioan_1_processed.json --index od $@
./od-upload.py -i ../data/ioan/ioan_2_processed.json --index od $@
./od-upload.py -i ../data/ioan/ioan_3_processed.json --index od $@
./od-upload.py -i ../data/ioan/ioan_4_processed.json --index od $@
./od-upload.py -i ../data/ioan/ioan_5_processed.json --index od $@
./od-upload.py -i ../data/ioan/ioan_6_processed.json --index od $@
./od-upload.py -i ../data/ioan/ioan_7_processed.json --index od $@