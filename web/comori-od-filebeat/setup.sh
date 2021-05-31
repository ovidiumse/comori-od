#!/bin/sh

filebeat setup -e -E setup.kibana.username="${ELASTIC_USER}" -E setup.kibana.password="${ELASTIC_PASSWORD}"