# coding: utf-8
from __future__ import unicode_literals
from django.db import models
from django.utils.html import mark_safe
from django.contrib.sites.models import Site
from markdown import markdown


class Entry(models.Model):
    author = models.ForeignKey('auth.User', related_name='news_entries')
    pub_date = models.DateTimeField(verbose_name='publication date', auto_now_add=True)
    title = models.CharField(max_length=100)
    text = models.TextField(help_text='Obsah bude prehnaný <a '
                            'href="http://en.wikipedia.org/wiki/Markdown">'
                            'Markdownom</a>.')
    slug = models.SlugField()
    sites = models.ManyToManyField(Site)

    class Meta:
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)
        verbose_name = 'novinka'
        verbose_name_plural = 'novinky'

    def __unicode__(self):
        return self.title

    def rendered_text(self):
        return mark_safe(markdown(self.text, safe_mode=False))
