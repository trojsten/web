# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models


class LevelSolved(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    semester = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        unique_together = ('user', 'semester', 'level')


class LevelSubmit(models.Model):
    status = models.CharField(max_length=3)
