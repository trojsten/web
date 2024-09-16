# -*- coding: utf-8 -*-
# Common settings for trojsten.
import json
import os
import sys

from django.contrib.messages import constants as messages
from django.core.files.storage import FileSystemStorage
from django.http import UnreadablePostError
from django.utils.translation import ugettext_lazy as _
from judge_client import client
from pymdownx import emoji

import trojsten.special.installed_apps

from . import site_config


def env(name, default):
    return os.environ.get(name, default)


def bool_env(name, default):
    val = str(env(name, default)).lower()
    return val == "true" or val == "1"


def skip_unreadable_post(record):
    if record.exc_info:
        exc_type, exc_value = record.exc_info[:2]
        if isinstance(exc_value, UnreadablePostError):
            return False
    return True


#
# Django settings
#

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("TROJSTENWEB_DATABASE_NAME", "trojsten"),
        "USER": env("TROJSTENWEB_DATABASE_USER", "trojsten"),
        "PASSWORD": env("TROJSTENWEB_DATABASE_PASSWORD", ""),
        "HOST": env("TROJSTENWEB_DATABASE_URL", ""),
        "PORT": env("TROJSTENWEB_DATABASE_PORT", ""),
    },
    "kaspar": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("TROJSTENWEB_KASPAR_DATABASE_NAME", "kaspar"),
        "USER": env("TROJSTENWEB_KASPAR_DATABASE_USER", "trojsten"),
        "PASSWORD": env("TROJSTENWEB_KASPAR_DATABASE_PASSWORD", ""),
        "HOST": env("TROJSTENWEB_KASPAR_DATABASE_URL", ""),
        "PORT": env("TROJSTENWEB_KASPAR_DATABASE_PORT", ""),
    },
}

if "test" in sys.argv:
    if "kaspar" in DATABASES:
        del DATABASES["kaspar"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "results-cache",
        "TIMEOUT": 60 * 5,
        "MAX_ENTRIES": 100,
    }
}

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(trojsten.__file__))
)

AUTH_USER_MODEL = "people.User"

DEBUG = bool_env("TROJSTENWEB_DEBUG", "False")

if "TROJSTENWEB_ADMINS" in os.environ:
    ADMINS = tuple([tuple(admin.split(":")) for admin in env("TROJSTENWEB_ADMINS", "").split(";")])
else:
    ADMINS = ()

if "TROJSTENWEB_MANAGERS" in os.environ:
    MANAGERS = tuple(
        [tuple(manager.split(":")) for manager in env("TROJSTENWEB_MANAGERS", "").split(";")]
    )
else:
    MANAGERS = ()

DEFAULT_FROM_EMAIL = "no-reply@trojsten.sk"

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env("TROJSTENWEB_ALLOWED_HOSTS", "www.ksp.sk").split(";")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = env("TROJSTENWEB_TIME_ZONE", "Europe/Bratislava")

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = env("TROJSTENWEB_LANGUAGE_CODE", "sk-SK")

SITE_ID = 1

SITES = site_config.SITES

NAVBAR_SITES = []

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

LOCALE_PATHS = (os.path.join(PROJECT_DIR, "locale"),)

APPEND_SLASH = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = env("TROJSTENWEB_MEDIA_ROOT", os.path.join(PROJECT_DIR, "media"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = env("TROJSTENWEB_MEDIA_URL", "/media/")

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = env("TROJSTENWEB_STATIC_ROOT", os.path.join(PROJECT_DIR, "static"))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = env("TROJSTENWEB_STATIC_URL", "/static/")

# Additional locations of static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env("TROJSTENWEB_SECRET_KEY", "*ev5i*d2v+ln+hm=swggoo-+%62y4*r8va@nign_mgq*&%x+z)")

# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "ksp_login.context_processors.login_providers_both",
                "trojsten.context_processors.current_site",
                "trojsten.context_processors.version_string",
            ]
        },
    }
]

CORS_ORIGIN_REGEX_WHITELIST = (
    "^(https?://)?(\w+\.)*ksp\.sk$",
    "^(https?://)?(\w+\.)*fks\.sk$",
    "^(https?://)?(\w+\.)*kms\.sk$",
    "^(https?://)?(\w+\.)*trojsten\.sk$",
)

MIDDLEWARE = (
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
)

ROOT_URLCONF = "trojsten.urls.default"
HOST_MIDDLEWARE_URLCONF_MAP = {}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "trojsten.wsgi.application"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "trojsten",
    "trojsten.utils",
    "trojsten.people",
    "trojsten.contests.apps.ContestsConfig",
    "trojsten.diplomas",
    "trojsten.events",
    "trojsten.submit.apps.SubmitConfig",
    "trojsten.results",
    "trojsten.rules",
    "trojsten.reviews",
    "trojsten.menu",
    "trojsten.threads",
    "trojsten.dbsanitizer",
    "trojsten.login",
    "trojsten.schools",
    "trojsten.polls",
    "trojsten.top30",
    "trojsten.contact_form",
    "trojsten.notifications.apps.NotificationsConfig",
    "django_countries",
    # Keep this under trojsten to let trojsten override templates.
    "news",
    "tips",
    "django.contrib.admin",
    "social_django",
    "ksp_login",
    "bootstrapform",
    "easy_select2",
    "mathfilters",
    "sortedm2m",
    "favicon",
    "import_export",
    "oauth2_provider",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "snowpenguin.django.recaptcha2",
    # django-wiki and its dependencies
    "django.contrib.humanize",
    "django_nyt",
    "mptt",
    "sekizai",
    "sorl.thumbnail",
    "wiki",
    "wiki.plugins.attachments",
    "wiki.plugins.notifications",
    "wiki.plugins.images",
    "wiki.plugins.macros",
    "taggit",
    "haystack",
    # django-fluent-comments and its dependencies
    "fluent_comments",
    "crispy_forms",
    "django_comments",
    "threadedcomments",
)

INSTALLED_APPS += trojsten.special.installed_apps.INSTALLED_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"}},
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "skip_unreadable_posts": {
            "()": "django.utils.log.CallbackFilter",
            "callback": skip_unreadable_post,
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false", "skip_unreadable_posts"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": True,
        },
        "management_commands": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}

# Override message tags for bootstrap 3 compatibility.
MESSAGE_TAGS = {messages.ERROR: "danger error"}

# The URL to which Django redirects as soon as login is required.
LOGIN_URL = "/ucet/login/"
LOGIN_ERROR_URL = "/ucet/login/"
LOGIN_REDIRECT_URL = "/ucet/"
TROJSTEN_LOGIN_PROVIDER_URL = env("TROJSTENWEB_LOGIN_PROVIDER_URL", "https://login.trojsten.sk")
# This is for internal bakend calls.
TROJSTEN_LOGIN_PROVIDER_INTERNAL_URL = env(
    "TROJSTENWEB_LOGIN_PROVIDER_INTERNAL_URL", TROJSTEN_LOGIN_PROVIDER_URL
)

#
# Included packages settings
#
FAVICON_PATH = STATIC_URL + "images/favicon.ico"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

# KSP-Login settings
# The list of authentication providers we want to allow.
LOGIN_PROVIDERS = ("trojsten.login.backends.TrojstenOAuth2",)

AUTHENTICATION_BACKENDS = LOGIN_PROVIDERS + ("django.contrib.auth.backends.ModelBackend",)

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "trojsten.login.pipeline.associate_by_uid",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
)

PROVIDER_OVERRIDE_DICT = json.loads(env("TROJSTENWEB_AUTHENTICATION_PROVIDER_OVERRIDE_DICT", "{}"))

# The number of authentication providers to show in the short list.
AUTHENTICATION_PROVIDERS_BRIEF = int(env("TROJSTENWEB_AUTHENTICATION_PROVIDERS_BRIEF", "3"))

# @TODO: nadefinovat vhodne scopy
OAUTH2_PROVIDER = {
    # this is the list of available scopes
    "SCOPES": {"read": "Read scope", "write": "Write scope", "groups": "Access to your groups", "openid": "", "email": "", "profile": ""}
}

# Common markdown settings
MARKDOWN_EXTENSIONS = [
    "attr_list",
    "codehilite",
    "sane_lists",
    "markdown.extensions.tables",
    "pymdownx.magiclink",
    "pymdownx.betterem",
    "pymdownx.tilde",
    "pymdownx.emoji",
    "pymdownx.tasklist",
    "pymdownx.superfences",
]

MARKDOWN_EXTENSIONS_CONFIGS = {
    "pymdownx.tilde": {"subscript": False},
    "pymdownx.emoji": {
        "emoji_index": emoji.gemoji,
        "alt": "unicode",
        "options": {"attributes": {"align": "absmiddle", "height": "20px", "width": "20px"}},
    },
}

MARKDOWN_SETTINGS = {
    "safe_mode": False,
    "output_format": "html5",
    "extensions": MARKDOWN_EXTENSIONS,
    "extension_configs": MARKDOWN_EXTENSIONS_CONFIGS,
}

NEWS_MARKDOWN_KWARGS = MARKDOWN_SETTINGS
TIPS_MARKDOWN_KWARGS = MARKDOWN_SETTINGS

# WIKI SETTINGS
# We use ksp_login to handle accounts.
WIKI_ACCOUNT_HANDLING = False
# We use sendfile for downloading files
WIKI_ATTACHMENTS_USE_SENDFILE = True
WIKI_MARKDOWN_SANITIZE_HTML = False
WIKI_MARKDOWN_KWARGS = dict(
    MARKDOWN_SETTINGS,
    extensions=MARKDOWN_EXTENSIONS + ["footnotes", "wikilinks"],
    extension_configs=dict(MARKDOWN_EXTENSIONS_CONFIGS, toc={"title": _("Table of Contents")}),
)
WIKI_EDITOR = "trojsten.markdown_editors.TrojstenMarkItUp"
WIKI_ATTACHMENTS_PATH = env(
    "TROJSTENWEB_WIKI_ATTACHMENTS_PATH", os.path.join(MEDIA_ROOT, "wiki_attachments/%aid/")
)
WIKI_ATTACHMENTS_EXTENSIONS = ["pdf", "doc", "odt", "docx", "txt", "jpg", "png", "gif"]
WIKI_CHECK_SLUG_URL_AVAILABLE = False

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "trojsten.search.haystack_custom_backend.AsciifoldingElasticSearchEngine",
        "URL": env("TROJSTENWEB_HAYSTACK_CONNECTIONS_URL", "http://127.0.0.1:9200/"),
        "INDEX_NAME": "haystack",
    }
}

ELASTICSEARCH_ANALYZER = {
    "ascii_analyser": {"tokenizer": "standard", "filter": ["standard", "asciifolding", "lowercase"]}
}

# Comments settings
COMMENTS_APP = "fluent_comments"
FLUENT_COMMENTS_EXCLUDE_FIELDS = ("url", "title", "email")
CRISPY_TEMPLATE_PACK = "bootstrap3"
FLUENT_COMMENTS_USE_EMAIL_NOTIFICATION = False

#
# Trojstenweb Settings
#

# Task statements settings
_TASK_STATEMENTS_PATH = env(
    "TROJSTENWEB_TASK_STATEMENTS_PATH", os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, "statements")
)
TASK_STATEMENTS_STORAGE = FileSystemStorage(location=_TASK_STATEMENTS_PATH)
TASK_STATEMENTS_TASKS_DIR = env("TROJSTENWEB_TASK_STATEMENTS_TASKS_DIR", "zadania")
TASK_STATEMENTS_PREFIX_TASK = env("TROJSTENWEB_TASK_STATEMENTS_PREFIX_TASK", "prikl")
TASK_STATEMENTS_SOLUTIONS_DIR = env("TROJSTENWEB_TASK_STATEMENTS_SOLUTIONS_DIR", "vzoraky")
TASK_STATEMENTS_PICTURES_DIR = env("TROJSTENWEB_TASK_STATEMENTS_PICTURES_DIR", "obrazky")
TASK_STATEMENTS_HTML_DIR = env("TROJSTENWEB_TASK_STATEMENTS_HTML_DIR", "html")
TASK_STATEMENTS_PDF = env("TROJSTENWEB_TASK_STATEMENTS_PDF", "zadania.pdf")
TASK_STATEMENTS_SOLUTIONS_PDF = env("TROJSTENWEB_TASK_STATEMENTS_SOLUTIONS_PDF", "vzoraky.pdf")
ALLOWED_PICTURE_EXT = {".jpg", ".png", ".gif", ".webp", ".svg"}

# Round progressbar settings
ROUND_PROGRESS_DEFAULT_CLASS = env("TROJSTENWEB_ROUND_PROGRESS_DEFAULT_CLASS", "progress-bar-info")
ROUND_PROGRESS_WARNING_DAYS = int(env("TROJSTENWEB_ROUND_PROGRESS_WARNING_DAYS", "14"))
ROUND_PROGRESS_WARNING_CLASS = env(
    "TROJSTENWEB_ROUND_PROGRESS_WARNING_CLASS", "progress-bar-warning"
)
ROUND_PROGRESS_DANGER_DAYS = int(env("TROJSTENWEB_ROUND_PROGRESS_DANGER_DAYS", "7"))
ROUND_PROGRESS_DANGER_CLASS = env("TROJSTENWEB_ROUND_PROGRESS_DANGER_CLASS", "progress-bar-danger")
FROZEN_RESULTS_PATH = env(
    "TROJSTENWEB_FROZEN_RESULTS_PATH",
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, "frozen_results"),
)

# Submit settings
SUBMIT_DEBUG = bool(int(env("TROJSTENWEB_SUBMIT_DEBUG", "0")))
SUBMIT_PATH = env(
    "TROJSTENWEB_SUBMIT_PATH", os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, "submits")
)
SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md", ".rtf", ".docx", ".odt"]
SUBMIT_DESCRIPTION_ALLOWED_MIMETYPES = [
    "application/pdf",
    "text/plain",
    "text/rtf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.oasis.opendocument.text",
]
UPLOADED_FILENAME_MAXLENGTH = int(env("TROJSTENWEB_UPLOADED_FILENAME_MAXLENGTH", "100000"))
PROTOCOL_FILE_EXTENSION = env("TROJSTENWEB_PROTOCOL_FILE_EXTENSION", ".protokol")
TESTER_URL = env("TROJSTENWEB_TESTER_URL", "experiment")
TESTER_PORT = int(env("TROJSTENWEB_TESTER_PORT", "12347"))
TESTER_WEB_IDENTIFIER = env("TROJSTENWEB_TESTER_WEB_IDENTIFIER", "TROJSTENWEBv2")
JUDGE_CLIENT = client.JudgeClient(TESTER_WEB_IDENTIFIER, TESTER_URL, TESTER_PORT)

# Rules settings
COMPETITION_RULES = {
    2: "trojsten.rules.ksp.KSPRules",
    3: "trojsten.rules.kspt.KSPTRules",
    4: "trojsten.rules.prask.PraskRules",
    5: "trojsten.rules.old_fks.FKSRules",
    6: "trojsten.rules.ufo.UFORules",
    7: "trojsten.rules.kms.KMSRules",
    8: "trojsten.rules.fx.FXRules",
    9: "trojsten.rules.susi.SUSIRules",
    10: "trojsten.rules.fks.FKSRules",
}
DEFAULT_COMPETITION_RULES = "trojsten.rules.default.CompetitionRules"

ELASTICSEARCH_TESTS = True

DEFAULT_SCHOOL_COUNTRY = "SK"

RECAPTCHA_PRIVATE_KEY = env("TROJSTENWEB_RECAPTCHA_PRIVATE_KEY", "")
RECAPTCHA_PUBLIC_KEY = env("TROJSTENWEB_RECAPTCHA_PUBLIC_KEY", "")

if "TROJSTENWEB_CONTACT_FORM_RECIPIENTS" in os.environ:
    CONTACT_FORM_RECIPIENTS = tuple(env("TROJSTENWEB_CONTACT_FORM_RECIPIENTS", "").split(";"))
else:
    CONTACT_FORM_RECIPIENTS = tuple([mail_tuple[1] for mail_tuple in MANAGERS])

# Diploma settings
DIPLOMA_PARTICIPANTS_ALLOWED_EXTENSIONS = [".csv", ".json"]

EDITOR_CONFIG = {"mode": "python", "lineWrapping": False, "lineNumbers": True, "tabSize": 4}

TROJSTEN_NOTIFICATION_CHANNELS = [
    {"key": "submit_reviewed", "name": _("Your submit was reviewed"), "icon": "thumbs-up"},
    {"key": "submit_updated", "name": _("Your submit was updated"), "icon": "pencil"},
    {"key": "round_started", "name": _("New round started"), "icon": "plus"},
]
