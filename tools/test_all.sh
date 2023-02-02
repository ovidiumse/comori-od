#!/bin/sh

CWD=`realpath $(dirname $0)`

${CWD}/od-search-test.py -o "${CWD}/../data/test_results" $@