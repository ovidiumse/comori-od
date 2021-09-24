FROM ubuntu:latest
COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install pypy3 virtualenv wget less curl build-essential pypy3-dev libssl-dev libev-dev

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN pypy3 get-pip.py
RUN pypy3 -m pip install --upgrade pip

RUN virtualenv -p pypy3 ve
RUN . ve/bin/activate
RUN pypy3 -m pip install -r requirements.txt

COPY comori-od-restapi.py .
COPY cfg.yaml .
COPY logging.conf .

CMD gunicorn -b 0.0.0.0:$VIRTUAL_PORT --worker-class=gevent --worker-connections=1000 --workers=1 "comori-od-restapi:load_app('cfg.yaml')"
