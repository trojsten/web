from trojsten.settings.production import *

SITE_ID = 10
NAVBAR_SITES = []

ROOT_URLCONF = "trojsten.urls.login"

MIDDLEWARE += ("oauth2_provider.middleware.OAuth2TokenMiddleware",)

AUTHENTICATION_BACKENDS = tuple(
    env(
        "TROJSTENWEB_AUTHENTICATION_BACKENDS",
        ";".join(
            (
                "ksp_login.backends.LaunchpadAuth",
                "social_core.backends.open_id.OpenIdAuth",
            )
        ),
    ).split(";")
) + (
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "ksp_login.pipeline.register_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
)

# Top secret keys for production settings
SOCIAL_AUTH_FACEBOOK_KEY = requiredenv("TROJSTENWEB_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = requiredenv("TROJSTENWEB_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"locale": "sk_SK", "fields": "id,name,email"}
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = requiredenv("TROJSTENWEB_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = requiredenv("TROJSTENWEB_GOOGLE_OAUTH2_SECRET")
SOCIAL_AUTH_GITHUB_KEY = requiredenv("TROJSTENWEB_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = requiredenv("TROJSTENWEB_GITHUB_SECRET")
SOCIAL_AUTH_GITHUB_SCOPE = ["email"]
