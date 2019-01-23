# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models


class LevelSolved(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    series = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        unique_together = ('user', 'series', 'level')


class LevelSubmit(models.Model):
    status = models.CharField(max_length=3)
