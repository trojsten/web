from __future__ import absolute_import
from trojsten.settings.common import *

DEBUG = False
TEMPLATE_DEBUG = False

SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

# Load local settings
try:
    from trojsten.settings.local import *
except ImportError:
    pass

ALLOWED_INCLUDE_ROOTS = (
    TASK_STATEMENTS_PATH,
)
