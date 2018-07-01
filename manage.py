#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import textwrap

import dotenv
from django.db import connection


if __name__ == "__main__":
    dotenv.read_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trojsten.settings.development")

    if 'migrate' in sys.argv:
        rename_submit_app_in_db()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
