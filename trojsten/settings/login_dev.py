from trojsten.settings.development import *

SITE_ID = 10
NAVBAR_SITES = []

ROOT_URLCONF = "trojsten.urls.login"

CORS_ORIGIN_ALLOW_ALL = True

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
) + ("oauth2_provider.backends.OAuth2Backend", "django.contrib.auth.backends.ModelBackend")

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "ksp_login.pipeline.register_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
)
