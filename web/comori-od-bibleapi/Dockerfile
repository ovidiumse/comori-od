FROM ubuntu:latest

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install pypy3 pypy3-venv wget curl less build-essential pypy3-dev

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN pypy3 -m venv .venv/comori-od-bibleapi
RUN . .venv/comori-od-bibleapi/bin/activate
ARG PYPY3=.venv/comori-od-bibleapi/bin/pypy3
RUN ${PYPY3} get-pip.py
RUN ${PYPY3} -m pip install -r requirements.txt

COPY . .

CMD .venv/comori-od-bibleapi/bin/gunicorn -b 0.0.0.0:9002 --worker-class=gevent --worker-connections=1000 --workers=1 "comori-od-bibleapi:load_app('data/bible.json')"
