#!/bin/bash

version=`python -c "import sys; print(sys.version)" | head -n1 | cut -c1`
if [ $version = 3 ]
then
    SOURCES="requirements.in"
else
    SOURCES="requirements.in requirements2.in"
fi

pip-compile $SOURCES -o requirements.txt
pip-compile $SOURCES requirements.devel.in -o requirements.devel.txt
