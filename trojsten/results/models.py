# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings


@python_2_unicode_compatible
class FrozenResults(models.Model):
    round = models.ForeignKey('contests.Round', verbose_name='kolo')
    is_single_round = models.BooleanField(verbose_name='vynechať predošlé kolá')
    category = models.ForeignKey('tasks.Category', blank=True, null=True, verbose_name='kolo')
    time = models.DateTimeField(auto_now_add=True, verbose_name='čas')

    class Meta:
        verbose_name = 'Zmrazená výsledkovka'
        verbose_name_plural = 'Zmrazené výsledkovky'

    def __str__(self):
        return '%s(%s) [%s]' % (
            self.round,
            'single' if self.is_single_round else 'multi',
            self.category,
        )


@python_2_unicode_compatible
class FrozenPoints(models.Model):
    task = models.ForeignKey('tasks.Task', verbose_name='úloha')
    description_points = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='body za popis')
    source_points = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='body za program')
    sum = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='body')

    class Meta:
        verbose_name = 'Zmrazené body za úlohu'
        verbose_name_plural = 'Zmrazené body za úlohy'

    def __str__(self):
        return '%s: Popis: %s, Program: %s' % (
            self.task,
            self.description_points,
            self.source_points,
        )


@python_2_unicode_compatible
class FrozenUserResult(models.Model):
    frozenresults = models.ForeignKey('FrozenResults', verbose_name='výsledkovka')
    original_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='pôvodný používateľ')
    rank = models.IntegerField(verbose_name='poradie')
    fullname = models.CharField(max_length=500, verbose_name='plné meno')
    school_year = models.IntegerField(verbose_name='ročník')
    school = models.ForeignKey('people.School', verbose_name='škola')
    previous_points = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='body z predošlých kôl')
    sum = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='suma')
    task_points = models.ManyToManyField(FrozenPoints, verbose_name='body za úlohy')

    class Meta:
        verbose_name = 'Zmrazený výsledok'
        verbose_name_plural = 'Zmrazené výsledky'

    def __str__(self):
        return '%s %s' % (
            self.frozenresults,
            self.fullname,
        )
