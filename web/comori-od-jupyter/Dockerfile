ARG tag
FROM ubuntu:${tag}

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common libhunspell-dev
RUN apt-get -y install python3 virtualenv wget less curl build-essential python3-dev libssl-dev jq

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install --upgrade pip

RUN virtualenv -p python3 ve
RUN . ve/bin/activate
RUN python3 -m pip install -r requirements.txt

RUN useradd -ms /bin/bash jupyter
USER jupyter

WORKDIR /home/jupyter

CMD python3 -m jupyterlab \
    --no-browser \
    --ip 0.0.0.0 \
    --ServerApp.port=8088 \
    --ServerApp.password_required=True \
    --ServerApp.password="${JUPYTER_PASSWORD}"