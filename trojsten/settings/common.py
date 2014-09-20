# Common settings for trojsten.
import os
import trojsten

# Celery settings
#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = ("trojsten.task_statements.handlers", )

# Django settings
PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(trojsten.__file__))
)

AUTH_USER_MODEL = 'people.User'
DEBUG = False
TEMPLATE_DEBUG = DEBUG
SUBMIT_PATH = ''
TASK_STATEMENTS_PATH = ''
TASK_STATEMENTS_REPO_PATH = ''
TESTER_URL = 'experiment'
TESTER_PORT = 12347

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': '',                      # Or path to database file if using sqlite3.
#        'USER': '',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#    }
#}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Bratislava'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sk-SK'

SITE_ID = 1

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
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'


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
SECRET_KEY = '*ev5i*d2v+ln+hm=swggoo-+%62y4*r8va@nign_mgq*&%x+z)'

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
)

ALLOWED_INCLUDE_ROOTS = (
    TASK_STATEMENTS_PATH,
)

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
    #'django.contrib.flatpages',
    #'south',
    #'social_auth',
    #'ksp_login',
    'django.contrib.admin',
    'trojsten',
    'trojsten.utils',
    'trojsten.regal.people',
    'trojsten.regal.contests',
    'trojsten.regal.tasks',
    'trojsten.submit',
    'trojsten.results',
    'trojsten.news',
    'trojsten.task_statements',

    # Keep this under trojsten to let trojsten override templates.
    'social.apps.django_app.default',
    'ksp_login',
    'bootstrapform',

    # django-wiki and its dependencies
    'django.contrib.humanize',
    'south',
    'django_notify',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki',
    'wiki.plugins.attachments',
    'wiki.plugins.notifications',
    'wiki.plugins.images',
    'wiki.plugins.macros',
    'taggit',
)

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
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
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
    #"trojsten.context_processors.current_site",
)

# The list of authentication backends we want to allow.
AUTHENTICATION_BACKENDS = (
    #'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOpenId',
    #'social.backends.github.GithubOAuth2',
    'ksp_login.backends.LaunchpadAuth',
    'social.backends.open_id.OpenIdAuth',
    'django.contrib.auth.backends.ModelBackend',
)

# The number of authentication providers to show in the short list.
AUTHENTICATION_PROVIDERS_BRIEF = 3

# The URL to which Django redirects as soon as login is required.
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URL = "/account/"

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'ksp_login.pipeline.register_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

SOUTH_MIGRATION_MODULES = {
    'taggit': 'taggit.south_migrations',
}

UPLOADED_FILENAME_MAXLENGTH = 100000
PROTOCOL_FILE_EXTENSION = '.protokol'

TASK_STATEMENTS_SUFFIX_YEAR = 'rocnik'
TASK_STATEMENTS_SUFFIX_ROUND = 'kolo'
TASK_STATEMENTS_TASKS_DIR = 'zadania'
TASK_STATEMENTS_PREFIX_TASK = 'prikl'
TASK_STATEMENTS_SOLUTIONS_DIR = 'vzoraky'
TASK_STATEMENTS_PICTURES_DIR = 'obrazky'
TASK_STATEMENTS_HTML_DIR = 'html'
TASK_STATEMENTS_PDF = 'zadania.pdf'
TASK_STATEMENTS_SOLUTIONS_PDF = 'vzoraky.pdf'
ALLOWED_PICTURE_EXT = {'.jpg', '.png', '.gif', '.webp', }

# We use ksp_login to handle accounts.
WIKI_ACCOUNT_HANDLING = False

WIKI_ATTACHMENTS_USE_SENDFILE = True


WIKI_MARKDOWN_KWARGS = {
    'safe_mode': False,
}
