# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, resolve
from django.core.validators import URLValidator
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy
from sortedm2m.fields import SortedManyToManyField


def validate_url(value):
    valid = False
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

    # Translators: original: Hodnota by mala byť externá URL, absolútna cesta alebo urlname začínajúce znakom "@"!
    raise ValidationError(ugettext_lazy(
        'The value should be an external URL, an absolute path' +
        ' or an urlname prefixed with "@"!'
    ))


@python_2_unicode_compatible
class MenuItem(models.Model):
    # Translators: original: názov
    name = models.CharField(max_length=64, verbose_name=ugettext_lazy('name'))
    url = models.CharField(
        max_length=196,
        # Translators: original: adresa
        verbose_name=ugettext_lazy('address'),
        validators=[validate_url],
        # Translators: original: Povolené tvary sú "http(s)://domain.com/path", "/absolute/path" a "@urlname".
        help_text=(ugettext_lazy(
            'Should be in a form of "http(s)://domain.com/path", ' +
            '"/absolute/path" or "@urlname".'
        )),
    )
    glyphicon = models.CharField(
        max_length=64, verbose_name='glyphicon')
    active_url_pattern = models.CharField(
        max_length=196, blank=True,
        # Translators: original: regulárne výrazy pre zvýraznenie
        verbose_name=ugettext_lazy('regular expressions for active item'),
        # Translators: original: Medzerou oddelené urlnames a regulárne výrazy, ktoré pri zhode s cestou zvýraznia aktuálnu položku.
        help_text=(ugettext_lazy(
            'Space separated regular expressions or urlnames' +
            'that matches all urlpaths of this menu item'
        )),
    )

    def __str__(self):
        return '%s [%s]' % (self.name, self.url)

    class Meta:
        # Translators: original: Položka v menu
        verbose_name = ugettext_lazy('Menu item')
        # Translators: original: Položky v menu
        verbose_name_plural = ugettext_lazy('Menu items')

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
            except:
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
        # Translators: original: názov
        verbose_name=ugettext_lazy('name'),
        # Translators: original: Zobrazí sa v menu pre všetky skupiny okrem prvej.
        help_text=ugettext_lazy(
            'The name of the first group will not be displayed.'),
    )
    staff_only = models.BooleanField(
        default=False,
        # Translators: original: iba pre vedúcich
        verbose_name=ugettext_lazy('organizers only')
    )
    # Translators: original: pozícia
    position = models.IntegerField(verbose_name=ugettext_lazy('position'))
    site = models.ForeignKey(
        Site,
        related_name='menu_groups',
        db_index=True,
        # Translators: original: stránka
        verbose_name=ugettext_lazy('site')
    )
    items = SortedManyToManyField(
        MenuItem,
        related_name='groups',
        # Translators: original: položky
        verbose_name=ugettext_lazy('items')
    )

    def __str__(self):
        return '%s #%d: %s' % (str(self.site), self.position, self.name)

    class Meta:
        # Translators: original: Skupina v menu
        verbose_name = ugettext_lazy('Menu group')
        # Translators: original: Skupiny v menu
        verbose_name_plural = ugettext_lazy('Menu groups')
        unique_together = ("position", "site")
