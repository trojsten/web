# coding: utf-8
from __future__ import unicode_literals

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import mark_safe
from markdown import markdown
from taggit.managers import TaggableManager


@python_2_unicode_compatible
class Entry(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='news_entries')
    pub_date = models.DateTimeField(verbose_name='publication date', auto_now_add=True)
    title = models.CharField(max_length=100)
    text = models.TextField(help_text='Obsah bude prehnaný <a '
                            'href="http://en.wikipedia.org/wiki/Markdown">'
                            'Markdownom</a>.')
    slug = AutoSlugField(populate_from='title', unique=True)
    sites = models.ManyToManyField(Site)
    tags = TaggableManager(blank=True)

    class Meta:
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

    def __str__(self):
        return self.title

    def rendered_text(self):
        return mark_safe(markdown(self.text, safe_mode=False))
