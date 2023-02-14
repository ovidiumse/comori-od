local:
	make -f Makefile.local build up

test:
	DOCKER_HOST=ssh://ubuntu-dev make -f Makefile.test build up

new:
	DOCKER_HOST=ssh://ubuntu-prod make -f Makefile.new build up

prod:
	DOCKER_HOST=ssh://comori-od make -f Makefile.prod build up