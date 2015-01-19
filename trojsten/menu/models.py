# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField


@python_2_unicode_compatible
class MenuItem(models.Model):
    name = models.CharField(max_length=64, verbose_name='názov')
    url = models.CharField(max_length=196, verbose_name='adresa')
    glyphicon = models.CharField(
        max_length=64, verbose_name='glyphicon')
    active_url_pattern = models.CharField(
        max_length=196, blank=True,
        verbose_name='regulárny výraz pre zvýraznenie')

    def __str__(self):
        return '%s [%s]' % (self.name, self.url)

    class Meta:
        verbose_name = 'Položka v menu'
        verbose_name_plural = 'Položky v menu'


@python_2_unicode_compatible
class MenuGroup(models.Model):
    name = models.CharField(max_length=64, verbose_name='názov')
    staff_only = models.BooleanField(
        default=False, verbose_name='iba pre vedúcich')
    position = models.IntegerField(verbose_name='pozícia')
    site = models.ForeignKey(
        Site,
        related_name='menu_groups',
        db_index=True,
        verbose_name='stránka')
    items = SortedManyToManyField(
        MenuItem,
        related_name='groups',
        verbose_name='položky')

    def __str__(self):
        return '%s #%d: %s' % (str(self.site), self.position, self.name)

    class Meta:
        verbose_name = 'Skupina v menu'
        verbose_name_plural = 'Skupina v menu'
        unique_together = ("position", "site")
