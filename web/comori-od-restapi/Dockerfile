FROM ubuntu:latest

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install pypy3 virtualenv wget less curl

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN pypy3 get-pip.py

RUN virtualenv -p pypy3 ve
RUN . ve/bin/activate
RUN pypy3 -m pip install -r requirements.txt

COPY comori-od-restapi.py .
COPY prod_cfg.yaml .
COPY logging.conf .

CMD ["gunicorn", "-b", "0.0.0.0:9000", "comori-od-restapi:load_app('prod_cfg.yaml')"]