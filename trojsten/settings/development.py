from __future__ import absolute_import
from trojsten.settings.common import *

# Celery settings
BROKER_URL = 'django://'

# Django settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'trojsten',
        'USER': 'trojsten',
        'PASSWORD': 'trojsten',
    },
    'kaspar': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'kaspar',
        'USER': 'trojsten',
        'PASSWORD': 'trojsten',
    },
}

SENDFILE_BACKEND = 'sendfile.backends.development'

DEBUG = True
TEMPLATE_DEBUG = True
SUBMIT_PATH = '/tmp'
TASK_STATEMENTS_REPO_PATH = '/tmp/task_statements'
TASK_STATEMENTS_PATH = '/var/www/zadania'
FROZEN_RESULTS_PATH = '/var/www/frozen_results'

INSTALLED_APPS += (
    'debug_toolbar',
    'kombu.transport.django',
)
MIDDLEWARE_CLASSES = (('debug_toolbar.middleware.DebugToolbarMiddleware',)
   + MIDDLEWARE_CLASSES)

INTERNAL_IPS = ('127.0.0.1',)

# Feedback mail sending via "contact_form" - SMTP must be set for production
# Send from: EMAIL_USE_TLS, EMAIL_HOST, EMAIL_PORT, DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# Send to: MANAGERS
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITES[SITE_ID]['URL'] = 'http://localhost:8000'
