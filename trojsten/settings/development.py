from __future__ import absolute_import
from trojsten.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = True
SUBMIT_DEBUG = True
SENDFILE_BACKEND = 'sendfile.backends.development'

# Django debug toolbar set-up
INSTALLED_APPS += (
    'debug_toolbar',
)
MIDDLEWARE_CLASSES = (('debug_toolbar.middleware.DebugToolbarMiddleware',)
   + MIDDLEWARE_CLASSES)

INTERNAL_IPS = ('127.0.0.1',)

# Dummy email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use localhost for first site route
SITES[SITE_ID]['URL'] = 'http://localhost:8000'

