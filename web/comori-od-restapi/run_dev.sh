#!/usr/bin/bash
. venv/bin/activate
gunicorn -b 0.0.0.0:9000 "comori-od-restapi:load_app('dev_cfg.yaml')" --reload
deactivate