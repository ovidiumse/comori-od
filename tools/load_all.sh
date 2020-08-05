#!/bin/sh

echo "Starting Bible API..."
$(cd ../web/comori-od-bibleapi && ./run_dev.sh) &

# Cugetari Nemuritoare
./load_cugetari_total.sh -d -c $@

# Istoria unei Jertfe
./load_istorii.sh $@

# Hristos - Marturia mea
./load_marturii.sh $@

# Meditatii la Evanghelia dupa Ioan
./load_ioan.sh $@

# Cantari Nemuritoare
./load_cantari.sh $@

# Hristos - Puterea Apostoliei
./load_hristos_puterea.sh $@