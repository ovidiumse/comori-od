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

prod:
	make -f Makefile.prod build up

prod_nginx:
	make -f Makefile.prod nginx

prod_data: import_books
	make -f Makefile.prod data

prod_init:
	make -f Makefile.prod init

import_books:
	cd ../../tools/ ; ./import_books.sh

solarmon:
	make -f Makefile.solarmon build up
