from django.db import models
from django.conf import settings


class UserLink(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='+',
        null=True,
        blank=True,
    )
    link = models.URLField(max_length=255, unique=True)
