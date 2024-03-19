prepare_bible:
	mkdir -p ../comori-od-restapi/data
	cp ../../data/bible/*.json ../comori-od-restapi/data/

local: prepare_bible
	make -f Makefile.local build up

local_data: import_books
	make -f Makefile.local data

local_bible: 
	make -f Makefile.local bible

local_init:
	make -f Makefile.local init

test: prepare_bible
	make -f Makefile.test build up

test_nginx:
	make -f Makefile.test nginx

test_data: import_books
	make -f Makefile.test data

test_bible: 
	make -f Makefile.test bible

test_init:
	make -f Makefile.test init

admin:
	make -f Makefile.admin build up

prod: prepare_bible
	make -f Makefile.comori-od build up

prod_nginx:
	make -f Makefile.comori-od nginx

prod_data: import_books
	make -f Makefile.comori-od data

prod_bible: 
	make -f Makefile.comori-od bible

prod_init:
	make -f Makefile.comori-od init

convert_books:
	cd ../../tools/ ; ./convert_books.sh

import_books:
	cd ../../tools/ ; ./import_books.sh

solarmon:
	make -f Makefile.solarmon build up
