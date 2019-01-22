#!/usr/bin/env bash

version=`python -c "import sys; print(sys.version)" | head -n1 | cut -c1`
if [ $version = 3 ]
then
    SOURCES="requirements.in"
    pip-compile -r $SOURCES -o requirements.txt
else
    echo "Python 2 is no longer supported."
fi

