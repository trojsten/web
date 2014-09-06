from __future__ import absolute_import
from trojsten.settings.common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'trojsten',
        'USER': 'trojsten',
        'PASSWORD': 'trojsten',
    },
}

SENDFILE_BACKEND = 'sendfile.backends.development'

DEBUG = True
TEMPLATE_DEBUG = True
SUBMIT_PATH = '/tmp'

INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES = (('debug_toolbar.middleware.DebugToolbarMiddleware',)
    + MIDDLEWARE_CLASSES)

INTERNAL_IPS = ('127.0.0.1',)
