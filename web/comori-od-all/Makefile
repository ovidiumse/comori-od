local:
	make -f Makefile.local build up

local_data: import_books
	make -f Makefile.local data

local_init:
	make -f Makefile.local init

test:
	make -f Makefile.test build up

test_nginx:
	make -f Makefile.text nginx

test_data: import_books
	make -f Makefile.test data

test_init:
	make -f Makefile.test init

admin:
	make -f Makefile.admin build up

prod:
	make -f Makefile.comori-od build up

prod_nginx:
	make -f Makefile.comori-od nginx

prod_data: import_books
	make -f Makefile.comori-od data

prod_init:
	make -f Makefile.comori-od init

convert_books:
	cd ../../tools/ ; ./convert_books.sh

import_books:
	cd ../../tools/ ; ./import_books.sh

solarmon:
	make -f Makefile.solarmon build up
