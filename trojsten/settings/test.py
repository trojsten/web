from __future__ import absolute_import

from trojsten.settings.common import *

DEBUG = False
SENDFILE_BACKEND = 'sendfile.backends.development'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
