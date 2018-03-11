from __future__ import absolute_import
import os

from trojsten.settings.common import *

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'results-cache',
    }
}

ALLOWED_HOSTS = ['*']
DEBUG = True
SUBMIT_DEBUG = True
# Disable captcha
os.environ['RECAPTCHA_DISABLE'] = 'True'
CRISPY_FAIL_SILENTLY = not DEBUG
SENDFILE_BACKEND = 'sendfile.backends.development'
DEBUG_TOOLBAR_PATCH_SETTINGS = False
SITE_ID = int(env('TROJSTENWEB_DEVELOPMENT_SITE_ID', 1))
ROOT_URLCONF = env('TROJSTENWEB_DEVELOPMENT_ROOT_URLCONF', 'trojsten.urls.default')
CORS_ORIGIN_ALLOW_ALL = True
ADMINS = MANAGERS = (('Admin', 'admin@localhost'),)

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
        'management_commands': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

TROJSTEN_LOGIN_PROVIDER_URL = env(
    'TROJSTENWEB_LOGIN_PROVIDER_URL',
    'http://localhost:8047',
)

SOCIAL_AUTH_TROJSTEN_KEY = env('TROJSTENWEB_LOGIN_KEY', '2uDyDhLKULKxzDyrpwabt0TLWsc2Weq9GaNUfwWD')
SOCIAL_AUTH_TROJSTEN_SECRET = env(
    'TROJSTENWEB_LOGIN_SECRET',
    '8osYrtZPMAMaWBmc3KePnyJ87euqrrcXZHbKPVbnLTWoR8MLCmNT1bqhIOsJbn6NK0WkQA19jePbyw7iGtdQ05Q1rbXja'
    'EaRtfDI9OHDlBVfd9CUM7Ve0lxdXjhI3Ldj'
)

ELASTICSEARCH_TESTS = bool(int(env('TROJSTENWEB_ELASTICSEARCH_TESTS', False)))
