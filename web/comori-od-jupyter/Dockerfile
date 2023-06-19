ARG tag
FROM ubuntu:${tag}

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common libhunspell-dev
RUN apt-get -y install python3 python3-venv wget less curl build-essential python3-dev libssl-dev jq

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 -m venv .venv/comori-od-jupyter
RUN . .venv/comori-od-jupyter/bin/activate
ARG PYTHON3=.venv/comori-od-jupyter/bin/python3
RUN ${PYTHON3} get-pip.py
RUN ${PYTHON3} -m pip install --upgrade pip
RUN ${PYTHON3} -m pip install -r requirements.txt

RUN useradd -ms /bin/bash jupyter
USER jupyter

WORKDIR /home/jupyter

CMD /.venv/comori-od-jupyter/bin/python3 -m jupyterlab \
    --no-browser \
    --ip 0.0.0.0 \
    --ServerApp.port=8088 \
    --ServerApp.password_required=True \
    --ServerApp.password="${JUPYTER_PASSWORD}"