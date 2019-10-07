from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

import trojsten.notifications.constants as notification_constants
from trojsten.people.models import User


class Subscription(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    status = models.IntegerField(_("Status"), choices=notification_constants.STATUSES)
    notification_type = models.PositiveIntegerField()
    send_emails = models.BooleanField(_("Send emails?"), default=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def __str__(self):
        if not self.content_type:
            return "%s (None) for %s" % (self.notification_type, self.user)
        return "%s (%s:%d) for %s" % (
            self.notification_type,
            self.content_type or None,
            self.object_id,
            self.user,
        )

    @property
    def target(self):
        """
        Target object of this subscription.
        ex. if you subscribe to news of Site(1), this will return the object Site(1).
        """
        if not self.content_type:
            return None
        return self.content_type.model_class().objects.get(pk=self.object_id)


class Notification(models.Model):
    subscription = models.ForeignKey(
        Subscription, verbose_name=_("Subscription"), on_delete=models.CASCADE
    )
    message = models.TextField()
    url = models.URLField(blank=True, null=True)

    was_read = models.BooleanField(default=False)
    was_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return "%s (%s)" % (self.message, self.subscription.user)
