# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import pytz
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.auth.models import Group

from uuidfield import UUIDField


class RoundManager(models.Manager):
    def visible(self, user):
        if user.is_superuser:
            return self.get_queryset()
        else:
            return self.filter(
                Q(series__competition__organizers_group__in=user.groups.all())
                | Q(visible=True)
            )

    def latest_visible(self, user):
        return self.visible(user).order_by(
            'series__competition', '-end_time'
        ).distinct(
            'series__competition'
        ).select_related(
            'series__competition'
        )


@python_2_unicode_compatible
class Repository(models.Model):
    notification_string = UUIDField(
        auto=True, primary_key=True, version=4, verbose_name='string pre push notifikáciu'
    )
    url = models.CharField(max_length=128, verbose_name='url git repozitára')

    class Meta:
        verbose_name = 'Repozitár'
        verbose_name_plural = 'Repozitáre'

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Competition(models.Model):
    '''
    Consists of series.
    '''
    name = models.CharField(max_length=128, verbose_name='názov')
    sites = models.ManyToManyField(Site)
    repo = models.ForeignKey(Repository, null=True, blank=True, verbose_name='git repozitár')
    repo_root = models.CharField(
        max_length=128, verbose_name='adresa foldra súťaže v repozitári'
    )
    organizers_group = models.ForeignKey(Group, null=True, verbose_name='skupina vedúcich')

    class Meta:
        verbose_name = 'Súťaž'
        verbose_name_plural = 'Súťaže'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Series(models.Model):
    '''
    Series consists of several rounds.
    '''
    competition = models.ForeignKey(Competition, verbose_name='súťaž')
    name = models.CharField(max_length=32, verbose_name='názov', blank=True)
    number = models.IntegerField(verbose_name='číslo série')
    year = models.IntegerField(verbose_name='ročník')

    class Meta:
        verbose_name = 'Séria'
        verbose_name_plural = 'Série'

    def __str__(self):
        return '%i. (%s) séria, %i. ročník %s'\
            % (self.number, self.name, self.year, self.competition)

    def short_str(self):
        return '%i. (%s) séria'\
            % (self.number, self.name)
    short_str.short_description = 'Séria'


@python_2_unicode_compatible
class Round(models.Model):
    '''
    Round has tasks.
    Holds information about deadline and such things
    '''
    series = models.ForeignKey(Series, verbose_name='séria')
    number = models.IntegerField(verbose_name='číslo')
    start_time = models.DateTimeField(
        verbose_name='začiatok', default=datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    )
    end_time = models.DateTimeField(
        verbose_name='koniec', default=datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        )
    )
    visible = models.BooleanField(verbose_name='viditeľnosť')
    solutions_visible = models.BooleanField(verbose_name='viditeľnosť vzorákov')

    objects = RoundManager()

    @property
    def can_submit(self):
        if datetime.now(pytz.utc) <= self.end_time:
            return True
        return False

    def get_base_path(self):
        round_dir = '{}{}'.format(self.number, settings.TASK_STATEMENTS_SUFFIX_ROUND)
        year_dir = '{}{}'.format(self.series.year, settings.TASK_STATEMENTS_SUFFIX_YEAR)
        competition_name = self.series.competition.name
        path = os.path.join(
            settings.TASK_STATEMENTS_PATH,
            competition_name,
            year_dir,
            round_dir,
        )
        return path

    def get_path(self, solution=False):
        path_type = settings.TASK_STATEMENTS_SOLUTIONS_DIR if solution\
            else settings.TASK_STATEMENTS_TASKS_DIR
        path = os.path.join(
            self.get_base_path(),
            path_type,
        )
        return path

    def get_pdf_path(self, solution=False):
        pdf_file = settings.TASK_STATEMENTS_SOLUTIONS_PDF if solution\
            else settings.TASK_STATEMENTS_PDF
        path = os.path.join(
            self.get_path(solution),
            pdf_file,
        )
        return path

    def get_pictures_path(self):
        path = os.path.join(
            self.get_base_path(),
            settings.TASK_STATEMENTS_PICTURES_DIR,
        )
        return path

    @property
    def tasks_pdf_exists(self):
        path = self.get_pdf_path(solution=False)
        return os.path.exists(path)

    @property
    def solutions_pdf_exists(self):
        path = self.get_pdf_path(solution=True)
        return os.path.exists(path)

    def is_visible_for_user(self, user):
        return (
            user.is_superuser or
            self.series.competition.organizers_group in user.groups.all() or
            self.visible
        )

    def solutions_are_visible_for_user(self, user):
        return (
            user.is_superuser or
            self.series.competition.organizers_group in user.groups.all() or
            self.solutions_visible
        )

    class Meta:
        verbose_name = 'Kolo'
        verbose_name_plural = 'Kolá'

    def __str__(self):
        return '%i. kolo, %i. séria, %i. ročník %s' % (
            self.number,
            self.series.number,
            self.series.year,
            self.series.competition,
        )

    def short_str(self):
        return '%i. kolo' % self.number
    short_str.short_description = 'kolo'
