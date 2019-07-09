#!/usr/bin/env python
from __future__ import print_function

import sys

import dotenv
import os

if __name__ == "__main__":
    dotenv.read_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trojsten.settings.development")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
