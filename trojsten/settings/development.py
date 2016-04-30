from __future__ import absolute_import

from trojsten.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = True
SUBMIT_DEBUG = True
SENDFILE_BACKEND = 'sendfile.backends.development'
DEBUG_TOOLBAR_PATCH_SETTINGS = False
SITE_ID = int(env('TROJSTENWEB_DEVELOPMENT_SITE_ID', 1))
ROOT_URLCONF = env('TROJSTENWEB_DEVELOPMENT_ROOT_URLCONF', 'trojsten.urls.default')
CORS_ORIGIN_ALLOW_ALL = True

# Django debug toolbar set-up
INSTALLED_APPS += (
    'debug_toolbar',
)
MIDDLEWARE_CLASSES = (
    ('debug_toolbar.middleware.DebugToolbarMiddleware',) +
    MIDDLEWARE_CLASSES
)

INTERNAL_IPS = ('127.0.0.1',)

# Dummy email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use localhost for first site route
SITES[SITE_ID].url = 'http://localhost:8000'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
