from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_nyt.models import NotificationType


class IgnoredNotifications(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = _("Ignored notification")
        verbose_name_plural = _("Ignored notifications")
