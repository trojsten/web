from django.conf import settings


def current_site(request):
    return {
        'SITE': settings.SITES[settings.SITE_ID],
        'OTHER_SITES': [v for k, v in sorted(settings.SITES.items()) if k != settings.SITE_ID],
    }
