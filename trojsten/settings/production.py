from django.core.exceptions import ImproperlyConfigured

from trojsten.settings.common import *


def requiredenv(name):
    if name not in os.environ:
        raise ImproperlyConfigured("Value %s missing in environment configuration" % name)
    return os.environ.get(name)


STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
SENDFILE_BACKEND = "sendfile.backends.xsendfile"

# Top secret keys for production settings
SOCIAL_AUTH_TROJSTEN_KEY = requiredenv("TROJSTENWEB_LOGIN_KEY")
SOCIAL_AUTH_TROJSTEN_SECRET = requiredenv("TROJSTENWEB_LOGIN_SECRET")
