# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve, reverse
from django.core.validators import URLValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from sortedm2m.fields import SortedManyToManyField


def validate_url(value):
    is_url = URLValidator()

    # External URL is valid
    try:
        is_url(value)
        return
    except ValidationError:
        pass

    # Absolute path is valid
    try:
        if value[:1] == '/':
            is_url('http://example.com' + value)
            return
    except ValidationError:
        pass

    # Urlname prefixed with @ is valid
    if value[:1] == '@':
        return

    raise ValidationError(
        'Hodnota by mala byť externá URL, absolútna cesta' +
        ' alebo urlname začínajúce znakom "@"!'
    )


@python_2_unicode_compatible
class MenuItem(models.Model):
    name = models.CharField(max_length=64, verbose_name='názov')
    url = models.CharField(
        max_length=196,
        verbose_name='adresa',
        validators=[validate_url],
        help_text=(
            'Povolené tvary sú "http(s)://domain.com/path", ' +
            '"/absolute/path" a "@urlname".'
        ),
    )
    glyphicon = models.CharField(
        max_length=64, verbose_name='glyphicon')
    active_url_pattern = models.CharField(
        max_length=196, blank=True,
        verbose_name='regulárne výrazy pre zvýraznenie',
        help_text=(
            'Medzerou oddelené urlnames a regulárne výrazy,' +
            'ktoré pri zhode s cestou zvýraznia aktuálnu položku.'
        ),
    )

    def __str__(self):
        return '%s [%s]' % (self.name, self.url)

    class Meta:
        verbose_name = 'Položka v menu'
        verbose_name_plural = 'Položky v menu'

    def get_url(self):
        if self.url[:1] == '@':
            return reverse(self.url[1:])
        return self.url

    def is_external(self):
        return self.url[:1] not in '@/'

    def is_active(self, url):
        for pattern in self.active_url_pattern.split():
            resolved = False
            try:
                resolved = resolve(url)
            except:  # noqa: E722 @FIXME
                pass

            matches = resolved and resolved.url_name == pattern

            if not matches:
                matches = bool(re.search(pattern, url))

            if matches:
                return True


@python_2_unicode_compatible
class MenuGroup(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name='názov',
        help_text='Zobrazí sa v menu pre všetky skupiny okrem prvej.',
    )
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
