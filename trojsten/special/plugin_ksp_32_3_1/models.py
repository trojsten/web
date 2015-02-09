# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings


class LevelSolved(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    series = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        unique_together = ('user', 'series', 'level')


class LevelSubmit(models.Model):
    status = models.CharField(max_length=3)
