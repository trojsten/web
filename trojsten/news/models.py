# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.html import mark_safe
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from markdown import markdown


@python_2_unicode_compatible
class Label(models.Model):
    name = models.CharField(
        max_length=128, verbose_name='názov', primary_key=True)

    class Meta:
        verbose_name = 'Štítok'
        verbose_name_plural = 'Štítky'

    def __str__(self):
        return str(self.name)


@python_2_unicode_compatible
class Entry(models.Model):
    author = models.ForeignKey('auth.User', related_name='news_entries')
    pub_date = models.DateTimeField(verbose_name='publication date', auto_now_add=True)
    title = models.CharField(max_length=100)
    text = models.TextField(help_text='Obsah bude prehnaný <a '
                            'href="http://en.wikipedia.org/wiki/Markdown">'
                            'Markdownom</a>.')
    slug = models.SlugField()
    sites = models.ManyToManyField(Site)
    labels = models.ManyToManyField(Label)

    class Meta:
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

    def __str__(self):
        return self.title

    def rendered_text(self):
        return mark_safe(markdown(self.text, safe_mode=False))
