from trojsten.settings.common import *

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": "results-cache",
    }
}

DEBUG = False
SENDFILE_BACKEND = "sendfile.backends.development"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
ADMINS = MANAGERS = (("Admin", "admin@example.com"),)

ELASTICSEARCH_TESTS = bool(int(env("TROJSTENWEB_ELASTICSEARCH_TESTS", True)))
