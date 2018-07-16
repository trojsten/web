# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .constants import FIELD_SEARCH_PATTERN
from .sources import SOURCE_CLASSES, SOURCE_CHOICES


class DiplomaDataSourceManager(models.Manager):
    def default(self):
        return self.get_queryset().filter(is_default=True) or []


@python_2_unicode_compatible
class DiplomaDataSource(models.Model):
    name = models.CharField(max_length=128, verbose_name='Source name')
    class_name = models.CharField(max_length=128, choices=SOURCE_CHOICES, verbose_name='Implemented source class')
    is_default = models.BooleanField(default=False, verbose_name="Add to predefined sources")

    objects = DiplomaDataSourceManager()

    @property
    def source_class(self):
        return SOURCE_CLASSES[self.class_name]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Zdroj dát pre diplomy'
        verbose_name_plural = 'Zdroje dát pre diplomy'


@python_2_unicode_compatible
class DiplomaTemplate(models.Model):
    name = models.CharField(max_length=128)
    svg = models.TextField()

    sources = models.ManyToManyField(DiplomaDataSource, blank=True)

    class Meta:
        verbose_name = 'Šablóna diplomu'
        verbose_name_plural = 'Šablóny diplomov'

    @property
    def editable_fields(self):
        return re.findall(FIELD_SEARCH_PATTERN, self.svg)

    def __str__(self):
        return self.name
