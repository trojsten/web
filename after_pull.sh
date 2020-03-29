#!/bin/bash
poetry install
python manage.py migrate
python manage.py compilemessages
