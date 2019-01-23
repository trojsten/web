from django.conf import settings
from django.db import models


class UserLink(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    link = models.URLField(max_length=255, unique=True)
