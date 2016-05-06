from __future__ import absolute_import

from trojsten.settings.production import *

SITE_ID = 10
NAVBAR_SITES = []

ROOT_URLCONF = 'trojsten.urls.login'

CORS_ORIGIN_REGEX_WHITELIST = (
    '^(https?://)?(\w+\.)*ksp\.sk$',
    '^(https?://)?(\w+\.)*fks\.sk$',
    '^(https?://)?(\w+\.)*kms\.sk$',
    '^(https?://)?(\w+\.)*trojsten\.sk$',
)
