FROM ubuntu:latest

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install pypy3 virtualenv wget

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN pypy3 get-pip.py

RUN virtualenv -p pypy3 ve
RUN . ve/bin/activate
RUN pypy3 -m pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:9001", "comori-od-bibleapi:load_app('data/bible.json')"]