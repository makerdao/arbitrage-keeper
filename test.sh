#!/bin/sh

PYTHONPATH=$PYTHONPATH:./lib/pymaker py.test --cov=arbitrage_keeper --cov-report=term --cov-append tests/
