# -*- coding: utf-8 -*-

import re
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .constants import FIELD_SEARCH_PATTERN


@python_2_unicode_compatible
class DiplomaTemplate(models.Model):
    name = models.CharField(max_length=128)
    svg = models.TextField()

    class Meta:
        verbose_name = 'Šablóna diplomu'
        verbose_name_plural = 'Šablóny diplomov'

    @property
    def editable_fields(self):
        return re.findall(FIELD_SEARCH_PATTERN, self.svg)

    def __str__(self):
        return self.name
