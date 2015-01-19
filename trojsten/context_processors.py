from django.conf import settings
from trojsten import version

def current_site(request):
    return {
        'SITE': settings.SITES[settings.SITE_ID],
        'OTHER_SITES': [v for k, v in sorted(settings.SITES.items()) if k != settings.SITE_ID],
    }

def version_string(request):
    return {
        'VERSION': version.version_string,
    }
