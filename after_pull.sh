#!/bin/bash
pip install -r requirements.devel.txt
python manage.py migrate
python manage.py compilemessages
