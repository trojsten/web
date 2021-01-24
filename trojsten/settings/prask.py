from trojsten.settings.production import *

SITE_ID = 2
NAVBAR_SITES = [1, 5]

SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS += [".ods", ".xlsx"]
SUBMIT_DESCRIPTION_ALLOWED_MIMETYPES += [
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]
