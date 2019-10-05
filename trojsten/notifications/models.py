from django.contrib.contenttypes.models import ContentType
from django.db import models

import trojsten.notifications.constants as notification_constants
from trojsten.people.models import User


class Subscription(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    status = models.IntegerField("Status", choices=notification_constants.STATUSES)
    notification_type = models.CharField("", max_length=50)
    send_emails = models.BooleanField("Send emails?", default=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return "%s (%s:%d) for %s" % (
            self.notification_type,
            self.content_type,
            self.object_id,
            self.user,
        )

    def get_target(self):
        return self.content_type.model_class().objects.get(pk=self.object_id)


class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, verbose_name="Subscription", on_delete=models.CASCADE
    )
    message = models.TextField()
    url = models.URLField(blank=True, null=True)

    was_read = models.BooleanField(default=False)
    was_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return "%s (%s)" % (self.message, self.user)
