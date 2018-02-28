#!/usr/bin/env bash

version=`python -c "import sys; print(sys.version)" | head -n1 | cut -c1`
if [ $version = 3 ]
then
    SOURCES="requirements.in"
    pip-compile -r $SOURCES -o requirements3.txt
    pip-compile -r $SOURCES requirements.devel.in -o requirements3.devel.txt
else
    SOURCES="requirements.in requirements2.in"
    pip-compile -r $SOURCES -o requirements.txt
    pip-compile -r $SOURCES requirements.devel.in -o requirements.devel.txt
fi

