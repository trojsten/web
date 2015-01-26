# -*- coding: utf-8 -*-

from django.conf import settings as s
import os

SPECIALS_ROOT = os.environ.get('TROJSTENWEB_SPECIALS_PATH',
    os.path.join(s.PROJECT_DIR, s.PROJECT_MODULE_NAME, 'specialne'))

DATA_ROOT = os.path.join(SPECIALS_ROOT, 'ksp', '32', '3', '1')