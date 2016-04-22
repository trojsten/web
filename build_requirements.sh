#!/bin/bash
pip-compile requirements.in
pip-compile requirements.in requirements.devel.in -o requirements.devel.txt
