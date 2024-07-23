FROM ubuntu:latest

COPY requirements.txt .

RUN apt-get update && \
	apt-get -y install apt-utils software-properties-common
RUN add-apt-repository ppa:pypy/ppa
RUN apt-get update && \
	apt-get -y install pypy3 pypy3-venv wget less curl build-essential pypy3-dev libssl-dev libev-dev

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN pypy3 -m venv .venv/comori-od-restapi
RUN . .venv/comori-od-restapi/bin/activate
ARG PYPY3=.venv/comori-od-restapi/bin/pypy3
RUN ${PYPY3} get-pip.py
RUN ${PYPY3} -m pip install --upgrade pip
RUN ${PYPY3} -m pip install -r requirements.txt

ADD data data
ADD api_utils api_utils
ADD aggregates_api aggregates_api
ADD authors_api authors_api
ADD articles_api articles_api
ADD content_api content_api
ADD favorites_api favorites_api
ADD index_api index_api
ADD markups_api markups_api
ADD mobileappsvc mobileappsvc
ADD mongoclient mongoclient
ADD readarticles_api readarticles_api
ADD recentlyadded_api recentlyadded_api
ADD recommended_api recommended_api
ADD tags_api tags_api
ADD titles_api titles_api
ADD users_api users_api
ADD odrefs_api odrefs_api
ADD bible_api bible_api

COPY comori-od-restapi.py .
COPY cfg.yaml .
COPY logging_cfg.yaml .

CMD .venv/comori-od-restapi/bin/gunicorn -b 0.0.0.0:9000 --worker-class=gevent --worker-connections=1000 --workers=1 "comori-od-restapi:load_app('cfg.yaml')"
