FROM ubuntu:latest

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install python3 python3-venv wget less curl build-essential python3-dev libssl-dev libev-dev unixodbc-dev

# install odbc driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 -m venv .venv/comori-od-logprocessor
RUN . .venv/comori-od-logprocessor/bin/activate
ARG PYTHON3=.venv/comori-od-logprocessor/bin/python3
RUN ${PYTHON3} get-pip.py
RUN ${PYTHON3} -m pip install --upgrade pip
RUN ${PYTHON3} -m pip install -r requirements.txt

ADD comori-od-logprocessor.py .
ADD cfg.yaml .
ADD logging_cfg.yaml .

CMD .venv/comori-od-logprocessor/bin/python3 comori-od-logprocessor.py