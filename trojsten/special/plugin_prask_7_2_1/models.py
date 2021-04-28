from django.conf import settings
from django.db import models


class UserLevel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    level_id = models.IntegerField()
    solved = models.BooleanField(default=False)
    used_hint = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "level_id"),)
