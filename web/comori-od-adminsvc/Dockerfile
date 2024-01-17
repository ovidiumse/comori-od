FROM ubuntu:latest

RUN apt-get update && \
	apt-get -y install wget curl apt-utils build-essential make pypy3 pypy3-dev python3 locales

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN curl -sSL https://get.docker.com/ | sh
RUN pypy3 get-pip.py
RUN pypy3 -m pip install --upgrade pip
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip

COPY requirements.txt .
RUN pypy3 -m pip install -r requirements.txt
RUN python3 -m pip install -r requirements.txt

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG C.UTF-8  
ENV LANGUAGE ""
ENV LC_ALL ""

COPY main.py .
RUN echo "\n[safe]" > /root/.gitconfig
RUN echo "\tdirectory = /comori-od/data" >> /root/.gitconfig

CMD gunicorn -b 0.0.0.0:8091 --workers=1 "main:main()" --timeout 300