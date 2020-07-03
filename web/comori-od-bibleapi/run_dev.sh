#!/usr/bin/bash
pypy3 -m venv venv
. venv/bin/activate
gunicorn -b 0.0.0.0:9001 "comori-od-bibleapi:load_app('data/bible.json')" --reload
deactivate