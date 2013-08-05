# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from trojsten.settings.common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'trojsten',
        'USER': 'trojsten',
    }
}

STATIC_ROOT = '/var/www/trojsten/static/'
MEDIA_ROOT = '/var/www/trojsten/media/'
MEDIA_URL = '/media/'

try:
    from trojsten.settings.local import *
except ImportError:
    pass
