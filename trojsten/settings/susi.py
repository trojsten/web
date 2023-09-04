from trojsten.settings.production import *

SITE_ID = 11
NAVBAR_SITES = [4, 1, 3, 5]

SUBMIT_DESCRIPTION_ALLOWED_EXTENSIONS += [".jpg", ".jpeg", ".png", ".pptx", ".gif", ".webp", ".avif"]
SUBMIT_DESCRIPTION_ALLOWED_MIMETYPES += [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/avif",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]
