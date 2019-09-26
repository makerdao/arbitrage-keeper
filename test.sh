#!/bin/bash

# Start ganache; record the PID so it can be cleanly stopped after testing
./lib/pymaker/ganache.sh &>/dev/null &
GANACHE_PID=$!
echo Started ganache as pid $GANACHE_PID
sleep 2

PYTHONPATH=$PYTHONPATH:./lib/pymaker py.test --cov=arbitrage_keeper --cov-report=term --cov-append tests/ -x
TEST_RESULT=$?

# Cleanup
pkill -P $GANACHE_PID

exit $TEST_RESULTu