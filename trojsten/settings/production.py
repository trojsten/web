from __future__ import absolute_import

from django.core.exceptions import ImproperlyConfigured

from trojsten.settings.common import *


def requiredenv(name):
    if name not in os.environ:
        raise ImproperlyConfigured("Value %s missing in environment configuration" % name)
    return os.environ.get(name)

DEBUG = False

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

# Top secret keys for production settings
SOCIAL_AUTH_FACEBOOK_KEY = requiredenv('TROJSTENWEB_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = requiredenv('TROJSTENWEB_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'sk_SK',
    'fields': 'id,name,email',
}
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = requiredenv('TROJSTENWEB_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = requiredenv('TROJSTENWEB_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GITHUB_KEY = requiredenv('TROJSTENWEB_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = requiredenv('TROJSTENWEB_GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_SCOPE = ['email']
SOCIAL_AUTH_TROJSTEN_KEY = requiredenv('TROJSTENWEB_LOGIN_KEY')
SOCIAL_AUTH_TROJSTEN_SECRET = requiredenv('TROJSTENWEB_LOGIN_SECRET')
