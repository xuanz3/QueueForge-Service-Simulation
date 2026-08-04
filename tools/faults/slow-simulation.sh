#!/bin/sh
set -eu
sleep "${QUEUEFORGE_FAULT_DELAY_SECONDS:-20}"
exec /usr/local/bin/queueforge-sim "$@"
