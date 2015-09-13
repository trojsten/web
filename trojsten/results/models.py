# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy
from django.db import models
from django.conf import settings


@python_2_unicode_compatible
class FrozenResults(models.Model):
    # Translators: original: série
    round = models.ForeignKey('contests.Round', verbose_name=ugettext_lazy('round'))
    # Translators: original: vynechať predošlé série
    is_single_round = models.BooleanField(verbose_name=ugettext_lazy('skip previous rounds'))
    # Translators: original: zahŕňa predošlé série
    has_previous_results = models.BooleanField(default=False, verbose_name=ugettext_lazy('include previous rounds'))
    # Translators: original: kategória
    category = models.ForeignKey('tasks.Category', blank=True, null=True, verbose_name=ugettext_lazy('category'))
    # Translators: original: čas
    time = models.DateTimeField(auto_now_add=True, verbose_name=ugettext_lazy('time'))

    class Meta:
        # Translators: original: Zmrazená výsledkovka
        verbose_name = ugettext_lazy('Frozen results')
        # Translators: original: Zmrazené výsledkovky
        verbose_name_plural = ugettext_lazy('Frozen results')

    def __str__(self):
        return '%s(%s) [%s]' % (
            self.round,
            'single' if self.is_single_round else 'multi',
            self.category,
        )


@python_2_unicode_compatible
class FrozenPoints(models.Model):
    # Translators: original: úloha
    task = models.ForeignKey('tasks.Task', verbose_name=ugettext_lazy('task'))
    # Translators: original: body za popis
    description_points = models.CharField(max_length=10, verbose_name=ugettext_lazy('points for description'))
    # Translators: original: body za program
    source_points = models.CharField(max_length=10, verbose_name=ugettext_lazy('points for program'))
    # Translators: original: body
    sum = models.CharField(max_length=10, verbose_name=ugettext_lazy('points'))

    class Meta:
        # Translators: original: Zmrazené body za úlohu
        verbose_name = ugettext_lazy('Frozen points for task')
        # Translators: original: Zmrazené body za úlohy
        verbose_name_plural = ugettext_lazy('Frozen points for tasks')

    def __str__(self):
        # Translators: original: %s: Popis: %s, Program: %s
        return ugettext_lazy('%s: Description: %s, Program: %s') % (
            self.task,
            self.description_points,
            self.source_points,
        )


@python_2_unicode_compatible
class FrozenUserResult(models.Model):
    # Translators: original: výsledkovka
    frozenresults = models.ForeignKey('FrozenResults', verbose_name=ugettext_lazy('results'))
    # Translators: original: pôvodný používateľ
    original_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=ugettext_lazy('original user'))
    # Translators: original: poradie
    rank = models.IntegerField(verbose_name=ugettext_lazy('rank'))
    # Translators: original: poradie
    prev_rank = models.IntegerField(verbose_name=ugettext_lazy('rank', blank=True, null=True))
    # Translators: original: plné meno
    fullname = models.CharField(max_length=500, verbose_name=ugettext_lazy('full name'))
    # Translators: original: ročník
    school_year = models.IntegerField(verbose_name=ugettext_lazy('grade'))
    # Translators: original: škola
    school = models.ForeignKey('people.School', verbose_name=ugettext_lazy('school'))
    # Translators: original: body z predošlých sérií
    previous_points = models.CharField(max_length=10, verbose_name=ugettext_lazy('points from previous rounds'))
    # Translators: original: suma
    sum = models.CharField(max_length=10, verbose_name=ugettext_lazy('sum'))
    # Translators: original: body za úlohy
    task_points = models.ManyToManyField(FrozenPoints, verbose_name=ugettext_lazy('points for tasks'))

    class Meta:
        # Translators: original: Zmrazený výsledok
        verbose_name = ugettext_lazy('Frozen result')
        # Translators: original: Zmrazené výsledky
        verbose_name_plural = ugettext_lazy('Frozen results')

    def __str__(self):
        return '%s %s' % (
            self.frozenresults,
            self.fullname,
        )
