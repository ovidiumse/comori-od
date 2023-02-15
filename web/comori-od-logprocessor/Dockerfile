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

ADD comori-od-logprocessor.py .
ADD cfg.yaml .
ADD logging_cfg.yaml .

CMD pypy3 comori-od-logprocessor.py