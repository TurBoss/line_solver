#!/usr/bin/env bash

set -e

[[ -z "$PYTHON" ]] && PYTHON="python"

#g++ -o ./hello ./libhello.cpp
#echo "=> now run the native one"
#./hello

g++ -o ./liblinesolver.so ./liblinesolver.cpp -fPIC -shared
#echo "=> now run the $PYTHON bound one"
#python hello.py