# -*- coding: utf-8 -*-

# Common settings for trojsten.
import os
import json
import trojsten
import trojsten.special.installed_apps

from django.http import UnreadablePostError

def env(name, default):
    return os.environ.get(name, default)

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
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('TROJSTENWEB_DATABASE_NAME', 'trojsten'),
        'USER': env('TROJSTENWEB_DATABASE_USER', 'trojsten'),
        'PASSWORD': env('TROJSTENWEB_DATABASE_PASSWORD', ''),
        'HOST': env('TROJSTENWEB_DATABASE_URL', ''),
        'PORT': env('TROJSTENWEB_DATABASE_PORT', ''),
    },
    'kaspar': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kaspar',
        'USER': 'trojsten',
        'PASSWORD': 'trojsten',
        'HOST': 'localhost',
        'PORT': '',
    },
}

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(trojsten.__file__))
)

AUTH_USER_MODEL = 'people.User'
DEBUG = bool(env('TROJSTENWEB_DEBUG', 'False'))
TEMPLATE_DEBUG = bool(env('TROJSTENWEB_TEMPLATE_DEBUG', DEBUG))

if 'TROJSTENWEB_ADMINS' in os.environ:
    ADMINS = tuple([tuple(admin.split(':')) for admin in env('TROJSTENWEB_ADMINS', '').split(';')])
else:
    ADMINS = ()

if 'TROJSTENWEB_MANAGERS' in os.environ:
    MANAGERS = tuple([
        tuple(manager.split(':'))
        for manager in env('TROJSTENWEB_MANAGERS', '').split(';')
    ])
else:
    MANAGERS = ()

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env('TROJSTENWEB_ALLOWED_HOSTS', 'www.ksp.sk').split(';')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = env('TROJSTENWEB_TIME_ZONE', 'Europe/Bratislava')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = env('TROJSTENWEB_LANGUAGE_CODE', 'sk-SK')

SITE_ID = 1

SITES = {
    1: {
        'NAME': 'Korešpondenčný seminár z programovania',
        'SHORT_NAME': 'KSP',
        'URL': 'http://ksp.sk',
        'HAS_LOGO': True,
        'FOLDER': 'ksp',
    },
    2: {
        'NAME': 'Prask',
        'SHORT_NAME': 'Prask',
        'URL': 'http://prask.ksp.sk',
        'HAS_LOGO': True,
        'FOLDER': 'prask',
    },
    3: {
        'NAME': 'Fyzikálny korešpondenčný seminár',
        'SHORT_NAME': 'FKS',
        'URL': 'http://fks.sk',
        'FOLDER': 'fks',
    },
    4: {
        'NAME': 'Korešpondenčný matematický seminár',
        'SHORT_NAME': 'KMS',
        'URL': 'http://kms.sk',
        'FOLDER': 'kms',
    },
    5: {
        'NAME': 'Trojsten',
        'SHORT_NAME': 'Trojsten',
        'URL': 'http://trojsten.sk',
        'FOLDER': 'trojsten',
    },
    6: {
        'NAME': 'Trojstenová Wikipédia',
        'SHORT_NAME': 'Wiki',
        'URL': 'http://wiki.trojsten.sk',
        'FOLDER': 'wiki',
    },
}


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

APPEND_SLASH = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = env('TROJSTENWEB_MEDIA_ROOT', os.path.join(PROJECT_DIR, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = env('TROJSTENWEB_MEDIA_URL', '/media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = env('TROJSTENWEB_STATIC_ROOT', os.path.join(PROJECT_DIR, 'static'))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = env('TROJSTENWEB_STATIC_URL', '/static/')


# Additional locations of static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('TROJSTENWEB_SECRET_KEY', '*ev5i*d2v+ln+hm=swggoo-+%62y4*r8va@nign_mgq*&%x+z)')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trojsten.middleware.multihostname.MultiHostnameMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)

ALLOWED_INCLUDE_ROOTS = ()

ROOT_URLCONF = 'trojsten.urls'
HOST_MIDDLEWARE_URLCONF_MAP = {}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'trojsten.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'trojsten',
    'trojsten.utils',
    'trojsten.regal.people',
    'trojsten.regal.contests',
    'trojsten.regal.tasks',
    'trojsten.regal.events',
    'trojsten.submit',
    'trojsten.results',
    'trojsten.reviews',
    'trojsten.news',
    'trojsten.archive',
    'trojsten.task_statements',
    'trojsten.menu',

    # Keep this under trojsten to let trojsten override templates.
    'django.contrib.admin',
    'social.apps.django_app.default',
    'ksp_login',
    'bootstrapform',
    'contact_form',
    'easy_select2',
    'mathfilters',
    'sortedm2m',

    # django-wiki and its dependencies
    'django.contrib.humanize',
    'south',
    'django_nyt',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki',
    'wiki.plugins.attachments',
    'wiki.plugins.notifications',
    'wiki.plugins.images',
    'wiki.plugins.macros',
    'taggit',
    'disqus',
    'kombu.transport.django',
)

INSTALLED_APPS += trojsten.special.installed_apps.INSTALLED_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'skip_unreadable_posts': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_unreadable_post,
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_unreadable_posts'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "sekizai.context_processors.sekizai",
    "ksp_login.context_processors.login_providers_both",
    "trojsten.context_processors.current_site",
    "trojsten.context_processors.version_string",
)

# Override message tags for bootstrap 3 compatibility.
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# The URL to which Django redirects as soon as login is required.
LOGIN_URL = "/ucet/login/"
LOGIN_ERROR_URL = "/ucet/login/"
LOGIN_REDIRECT_URL = "/ucet/"


#
# Included packages settings
#


# KSP-Login settings
# The list of authentication backends we want to allow.
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

PROVIDER_OVERRIDE_DICT = json.loads(env('TROJSTENWEB_AUTHENTICATION_PROVIDER_OVERRIDE_DICT', '{}'))

# The number of authentication providers to show in the short list.
AUTHENTICATION_PROVIDERS_BRIEF = int(env('TROJSTENWEB_AUTHENTICATION_PROVIDERS_BRIEF', '3'))

DISQUS_WEBSITE_SHORTNAME = env('TROJSTENWEB_DISQUS_WEBSITE_SHORTNAME', 'trojsten-ksp')

SOUTH_MIGRATION_MODULES = {
    'taggit': 'taggit.south_migrations',
    'django_nyt': 'django_nyt.south_migrations',
    'wiki': 'wiki.south_migrations',
    'images': 'wiki.plugins.images.south_migrations',
    'notifications': 'wiki.plugins.notifications.south_migrations',
    'attachments': 'wiki.plugins.attachments.south_migrations',
}

# WIKI SETTINGS
# We use ksp_login to handle accounts.
WIKI_ACCOUNT_HANDLING = False
# We use sendfile for downloading files
WIKI_ATTACHMENTS_USE_SENDFILE = True
WIKI_MARKDOWN_KWARGS = {
    'safe_mode': False,
}
WIKI_EDITOR = 'trojsten.markdown_editors.TrojstenMarkItUp'
WIKI_ATTACHMENTS_PATH = env(
    'TROJSTENWEB_WIKI_ATTACHMENTS_PATH',
    os.path.join(MEDIA_ROOT, 'wiki_attachments/%aid/')
)
WIKI_ATTACHMENTS_EXTENSIONS = ['pdf', 'doc', 'odt', 'docx', 'txt', 'jpg', 'png', 'gif']
WIKI_CHECK_SLUG_URL_AVAILABLE = False

# Celery settings
#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = ("trojsten.task_statements.handlers", )
BROKER_URL = env('TROJSTENWEB_CELERY_BROKER_URL', 'django://')

#
# Trojstenweb Settings
#

# Task statements settings
TASK_STATEMENTS_PATH = env('TROJSTENWEB_TASK_STATEMENTS_PATH', os.path.join(
    PROJECT_DIR, PROJECT_MODULE_NAME, 'statements')
)
TASK_STATEMENTS_REPO_PATH = env(
    'TROJSTENWEB_TASK_STATEMENTS_REPO_PATH',
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'statements_repo')
)
TASK_STATEMENTS_SUFFIX_YEAR = env('TROJSTENWEB_TASK_STATEMENTS_SUFFIX_YEAR', 'rocnik')
TASK_STATEMENTS_SUFFIX_ROUND = env('TROJSTENWEB_TASK_STATEMENTS_SUFFIX_ROUND', 'kolo')
TASK_STATEMENTS_TASKS_DIR = env('TROJSTENWEB_TASK_STATEMENTS_TASKS_DIR', 'zadania')
TASK_STATEMENTS_PREFIX_TASK = env('TROJSTENWEB_TASK_STATEMENTS_PREFIX_TASK', 'prikl')
TASK_STATEMENTS_SOLUTIONS_DIR = env('TROJSTENWEB_TASK_STATEMENTS_SOLUTIONS_DIR', 'vzoraky')
TASK_STATEMENTS_PICTURES_DIR = env('TROJSTENWEB_TASK_STATEMENTS_PICTURES_DIR', 'obrazky')
TASK_STATEMENTS_HTML_DIR = env('TROJSTENWEB_TASK_STATEMENTS_HTML_DIR', 'html')
TASK_STATEMENTS_PDF = env('TROJSTENWEB_TASK_STATEMENTS_PDF', 'zadania.pdf')
TASK_STATEMENTS_SOLUTIONS_PDF = env('TROJSTENWEB_TASK_STATEMENTS_SOLUTIONS_PDF', 'vzoraky.pdf')
ALLOWED_PICTURE_EXT = {'.jpg', '.png', '.gif', '.webp', }

# Round progressbar settings
ROUND_PROGRESS_DEFAULT_CLASS = env('TROJSTENWEB_ROUND_PROGRESS_DEFAULT_CLASS', 'progress-bar-info')
ROUND_PROGRESS_WARNING_DAYS = int(env('TROJSTENWEB_ROUND_PROGRESS_WARNING_DAYS', '14'))
ROUND_PROGRESS_WARNING_CLASS = env(
    'TROJSTENWEB_ROUND_PROGRESS_WARNING_CLASS', 'progress-bar-warning'
)
ROUND_PROGRESS_DANGER_DAYS = int(env('TROJSTENWEB_ROUND_PROGRESS_DANGER_DAYS', '7'))
ROUND_PROGRESS_DANGER_CLASS = env('TROJSTENWEB_ROUND_PROGRESS_DANGER_CLASS', 'progress-bar-danger')
FROZEN_RESULTS_PATH = env(
    'TROJSTENWEB_FROZEN_RESULTS_PATH',
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'frozen_results')
)

# Submit settings
SUBMIT_DEBUG = bool(int(env('TROJSTENWEB_SUBMIT_DEBUG', '0')))
SUBMIT_PATH = env('TROJSTENWEB_SUBMIT_PATH', os.path.join(
    PROJECT_DIR, PROJECT_MODULE_NAME, 'submits')
)
SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.md', '.rtf', '.doc', '.docx', '.odt']
UPLOADED_FILENAME_MAXLENGTH = int(env('TROJSTENWEB_UPLOADED_FILENAME_MAXLENGTH', '100000'))
PROTOCOL_FILE_EXTENSION = env('TROJSTENWEB_PROTOCOL_FILE_EXTENSION', '.protokol')
TESTER_URL = env('TROJSTENWEB_TESTER_URL', 'experiment')
TESTER_PORT = int(env('TROJSTENWEB_TESTER_PORT', '12347'))
TESTER_WEB_IDENTIFIER = env('TROJSTENWEB_TESTER_WEB_IDENTIFIER', 'KSP')

ALLOWED_INCLUDE_ROOTS += (
    TASK_STATEMENTS_PATH,
)
