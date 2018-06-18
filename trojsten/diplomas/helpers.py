# -*- coding: utf-8 -*-
import csv
import json
import os
import io
from django.utils.translation import ugettext_lazy as _

DECODE_ERROR_MSG = _("Unsupported file format")


def parse_participants(pfile):
    extension = os.path.splitext(pfile.name)[-1].lower()
    if extension == '.json':
        data = pfile.read()
        try:
            return json.loads(data), ""
        except json.JSONDecodeError:
            return None, DECODE_ERROR_MSG

    elif extension == '.csv':
        f = io.StringIO(pfile.read().decode())
        reader = csv.DictReader(f, dialect='excel-tab')
        try:
            return [dict(row) for row in reader], ""
        except csv.Error as e:
            print(e)
            return None, DECODE_ERROR_MSG
    else:
        return None, _("Unsupported extension")
