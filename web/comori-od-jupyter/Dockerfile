FROM ubuntu:latest

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common libhunspell-dev
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install pypy3 virtualenv wget less curl build-essential pypy3-dev libssl-dev jq

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN pypy3 get-pip.py
RUN pypy3 -m pip install --upgrade pip

RUN virtualenv -p pypy3 ve
RUN . ve/bin/activate
RUN pypy3 -m pip install -r requirements.txt

RUN useradd -ms /bin/bash jupyter
USER jupyter

WORKDIR /home/jupyter

CMD pypy3 -m jupyterlab \
    --no-browser \
    --ip 0.0.0.0 \
    --ServerApp.port=8088 \
    --ServerApp.password_required=True \
    --ServerApp.password="${JUPYTER_PASSWORD}"