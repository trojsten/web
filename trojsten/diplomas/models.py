# -*- coding: utf-8 -*-

import re
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .constants import FIELD_SEARCH_PATTERN
from .sources import get_class


@python_2_unicode_compatible
class DiplomaDataSource(models.Model):
    name = models.CharField(max_length=128)
    value = models.CharField(max_length=128)

    @property
    def source_class(self):
        return get_class(self.value)

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
