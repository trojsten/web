# -*- coding: utf-8 -*-
# Common constants for submit

from django.utils.translation import ugettext_lazy as _

SUBMIT_STATUS_REVIEWED = "reviewed"
SUBMIT_STATUS_IN_QUEUE = "in queue"
SUBMIT_STATUS_FINISHED = "finished"
SUBMIT_STATUS_OK = "OK"
SUBMIT_STATUS_CHOICES = [
    (SUBMIT_STATUS_REVIEWED, _("reviewed")),
    (SUBMIT_STATUS_IN_QUEUE, _("in queue")),
    (SUBMIT_STATUS_FINISHED, _("finished")),
    (SUBMIT_STATUS_OK, _("OK")),  # for support of old interactive tasks
]
SUBMIT_RAW_FILE_EXTENSION = ".raw"
SUBMIT_SOURCE_FILE_EXTENSION = ".data"
SUBMIT_TYPE_SOURCE = 0
SUBMIT_TYPE_DESCRIPTION = 1
SUBMIT_TYPE_TESTABLE_ZIP = 2
SUBMIT_TYPE_EXTERNAL = 3
SUBMIT_TYPE_TEXT = 4
SUBMIT_TYPES = [
    (SUBMIT_TYPE_SOURCE, "source"),
    (SUBMIT_TYPE_DESCRIPTION, "description"),
    (SUBMIT_TYPE_TESTABLE_ZIP, "testable_zip"),
    (SUBMIT_TYPE_EXTERNAL, "external"),
    (SUBMIT_TYPE_TEXT, "text"),
]
VIEWABLE_EXTENSIONS = [".pdf", ".txt"]

SUBMIT_VERBOSE_RESPONSE = {
    "WA": _("Wrong answer"),
    "CERR": _("Compilation error"),
    "TLE": _("Time limit exceeded"),
    "MLE": _("Memory limit exceeded"),
    "OK": _("OK"),
    "EXC": _("Runtime exception"),
    "SEC": _("Security exception"),
    "IGN": _("Ignored"),
    "PROTCOR": _("Protocol corrupted"),
}

SUBMIT_PAPER_FILEPATH = "<PAPIEROVE>"

EXT_MAPPING = {
    ".cpp": ".cc",
    ".cc": ".cc",
    ".pp": ".pas",
    ".pas": ".pas",
    ".dpr": ".pas",
    ".c": ".c",
    ".py": ".py",
    ".py3": ".py",
    ".hs": ".hs",
    ".cs": ".cs",
    ".java": ".java",
    ".zip": ".zip",
}

# How many points will be assigned for submit
SUSI_POINTS_ALLOCATION = {
    "Full": 6,
    "Small Hint": 4,
    "Big Hint": 2,
    "Incorrect": 0,
}

# How many days before end of the round will the hints be revealed
SUSI_HINT_DATES = {
    "Small Hint": 7,
    "Big Hint": 3,
}

SUSI_WRONG_SUBMITS_TO_PENALTY = 5
