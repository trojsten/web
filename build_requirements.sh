#!/bin/bash
pip-compile requirements.in requirements2.in -o requirements.txt
pip-compile requirements.in requirements2.in requirements.devel.in -o requirements.devel.txt
