# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site


@python_2_unicode_compatible
class Thread(models.Model):
    """
    Placeholder model for conversation.
    """

    title = models.CharField(max_length=100)
    sites = models.ManyToManyField(Site)

    class Meta:
        verbose_name = 'diskusné vlákno'
        verbose_name_plural = 'diskusné vlákna'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('thread', kwargs={'thread_id': self.id})
