from django.conf import settings

CHANNELS = getattr(settings, "TROJSTEN_NOTIFICATION_CHANNELS", [])
