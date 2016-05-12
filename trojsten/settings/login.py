from __future__ import absolute_import

# @TODO: switch back before production
# from trojsten.settings.production import *
from trojsten.settings.development import *

SITE_ID = 10
NAVBAR_SITES = []

ROOT_URLCONF = 'trojsten.urls.login'

CORS_ORIGIN_REGEX_WHITELIST = (
    '^(https?://)?(\w+\.)*ksp\.sk$',
    '^(https?://)?(\w+\.)*fks\.sk$',
    '^(https?://)?(\w+\.)*kms\.sk$',
    '^(https?://)?(\w+\.)*trojsten\.sk$',
)

MIDDLEWARE_CLASSES += (
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
)

AUTHENTICATION_BACKENDS = tuple(env('TROJSTENWEB_AUTHENTICATION_BACKENDS', ';'.join((
    'social.backends.google.GoogleOpenId',
    'ksp_login.backends.LaunchpadAuth',
    'social.backends.open_id.OpenIdAuth',
))).split(';')) + (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'ksp_login.pipeline.register_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
)

AUTHENTICATION_BACKENDS = tuple(env('TROJSTENWEB_AUTHENTICATION_BACKENDS', ';'.join((
    'social.backends.google.GoogleOpenId',
    'ksp_login.backends.LaunchpadAuth',
    'social.backends.open_id.OpenIdAuth',
    'django.contrib.auth.backends.ModelBackend',
))).split(';'))

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'ksp_login.pipeline.register_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
)
