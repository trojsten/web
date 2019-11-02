from django.db import models
from django.utils.translation import ugettext_lazy as _

from trojsten.people.models import User


class UnsubscribedChannel(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    channel = models.CharField(max_length=50)

    class Meta:
        verbose_name = _("Unsubscribed channel")
        verbose_name_plural = _("Unsubscribed channels")

    def __str__(self):
        return "%s @ %s" % (self.channel, self.user)


class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    channel = models.CharField(max_length=50)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)

    was_read = models.BooleanField(default=False)
    was_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return "%s (%s)" % (self.message, self.user)
