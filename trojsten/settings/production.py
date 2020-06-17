import warnings

from django.core.exceptions import ImproperlyConfigured

from trojsten.settings.common import *


def requiredenv(name):
    if name not in os.environ:
        warnings.warn("Value %s missing in environment configuration" % name)
    return os.environ.get(name)


STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
SENDFILE_BACKEND = "sendfile.backends.xsendfile"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("TROJSTENWEB_EMAIL_HOST", "localhost")
EMAIL_PORT = env("TROJSTENWEB_EMAIL_PORT", 25)
EMAIL_HOST_USER = env("TROJSTENWEB_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("TROJSTENWEB_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = bool_env("TROJSTENWEB_EMAIL_USE_TLS", True)

# Top secret keys for production settings
SOCIAL_AUTH_TROJSTEN_KEY = requiredenv("TROJSTENWEB_LOGIN_KEY")
SOCIAL_AUTH_TROJSTEN_SECRET = requiredenv("TROJSTENWEB_LOGIN_SECRET")
