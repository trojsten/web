#!/usr/bin/env python
import os
import sys
import textwrap

import dotenv
from django.db import connection


# TODO(mio): Remove this once it's deployed everywhere.
def rename_submit_app_in_db():
    check_sql = "SELECT * FROM django_content_type WHERE app_label = 'old_submit';"
    sql = textwrap.dedent("""\
        BEGIN;
        UPDATE django_migrations SET app = 'old_submit' WHERE app = 'submit';
        UPDATE django_content_type SET app_label = 'old_submit' WHERE app_label = 'submit';
        ALTER TABLE submit_submit RENAME TO old_submit_submit;
        ALTER TABLE submit_externalsubmittoken RENAME TO old_submit_externalsubmittoken;
        COMMIT;""")
    with connection.cursor() as cursor:
        cursor.execute(check_sql)
        if cursor.rowcount == 0:
            cursor.execute(sql)


if __name__ == "__main__":
    dotenv.read_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trojsten.settings.development")

    if 'migrate' in sys.argv:
        rename_submit_app_in_db()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
