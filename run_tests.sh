#!/bin/bash
export PYTHONPATH="$PYTHONPATH${PYTHONPATH+:}$PWD"
exec nosetest --with-doctest
