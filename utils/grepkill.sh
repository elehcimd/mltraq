#!/bin/bash

# Dirty and quick utility to kill processes that match a pattern in their name.
# E.g., ./grepkill.sh "mltraq dss"

PATTERN="$@"
echo "Killing processes matching pattern \"$PATTERN\" ..."
pids=$(ps aux | grep "$PATTERN" | grep -v grep | tr -s ' ' | cut -f2 -d' ')
if [ -z "$pids" ]
then
  echo "No matching processes, exiting."
else
  echo "Killing $pids ..."
  kill -9 $pids
fi

