#!/usr/bin/bash
pypy3 -m venv venv
. venv/bin/activate
pypy3 -m pip install -r requirements.txt
deactivate