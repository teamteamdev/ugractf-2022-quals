#!/bin/sh

./app/server.py "$1"
if [ "$?" = "139" ]; then
  echo "Segmentation fault"
fi
