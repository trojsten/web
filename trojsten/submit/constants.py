# -*- coding: utf-8 -*-
# Common constants for submit

from django.utils.translation import ugettext_lazy as _

SUBMIT_STATUS_REVIEWED = 'reviewed'
SUBMIT_STATUS_IN_QUEUE = 'in queue'
SUBMIT_STATUS_FINISHED = 'finished'
SUBMIT_RESPONSE_ERROR = 'CERR'
SUBMIT_RESPONSE_OK = 'OK'
SUBMIT_RAW_FILE_EXTENSION = '.raw'
SUBMIT_SOURCE_FILE_EXTENSION = '.data'
VIEWABLE_EXTENSIONS = ['.pdf', '.txt']

SUBMIT_VERBOSE_RESPONSE = {
    'WA': _('Wrong answer'),
    'CERR': _('Compilation error'),
    'TLE': _('Time limit exceeded'),
    'OK': _('OK'),
    'EXC': _('Runtime exception'),
    'SEC': _('Security exception'),
    'IGN': _('Ignored')
}
