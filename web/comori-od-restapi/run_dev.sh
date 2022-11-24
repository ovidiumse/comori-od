#!/usr/bin/bash
pypy3 -m venv venv
. venv/bin/activate
gunicorn -b 0.0.0.0:9000 "comori-od-restapi:load_app('cfg.yaml')" --reload
deactivate