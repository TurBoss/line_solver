#!/usr/bin/env bash

set -e

[[ -z "$PYTHON" ]] && PYTHON="python"

g++ -g -o ./main ./src/liblinesolver.cpp
g++ -o ./liblinesolver.so ./src/liblinesolver.cpp -fPIC -shared
# gdb main