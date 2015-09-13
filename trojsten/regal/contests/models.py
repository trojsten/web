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
from django.utils.translation import ugettext_lazy

from uuidfield import UUIDField

from trojsten.results.models import FrozenResults
from trojsten.rules import get_rules_for_competition
from trojsten.utils import utils


class RoundManager(models.Manager):
    def visible(self, user, all_sites=False):
        '''Returns only rounds visible for user
        '''
        if all_sites:
            competitions = Competition.objects.all()
        else:
            competitions = Competition.objects.current_site_only()

        res = self.filter(series__competition__in=competitions)
        if not user.is_superuser:
            res = res.filter(
                Q(series__competition__organizers_group__in=user.groups.all())
                | Q(visible=True)
            )
        return res

    def latest_visible(self, user, all_sites=False):
        '''Returns latest visible round for each competition
        '''
        return self.visible(user, all_sites).order_by(
            'series__competition', '-end_time', '-number',
        ).distinct(
            'series__competition'
        ).select_related(
            'series__competition'
        )

    def active_visible(self, user, all_sites=False):
        '''Returns all visible running rounds for each competition
        '''
        return self.visible(user, all_sites).filter(
            end_time__gte=datetime.now()
        ).order_by(
            '-end_time', '-number',
        ).select_related(
            'series__competition'
        )


class CompetitionManager(models.Manager):
    def current_site_only(self):
        '''Returns only competitions belonging to current site
        '''
        return Site.objects.get(pk=settings.SITE_ID).competition_set.all()


@python_2_unicode_compatible
class Repository(models.Model):
    notification_string = UUIDField(
        auto=True, primary_key=True, version=4,
        # Translators: original: string pre push notifikáciu
        verbose_name=ugettext_lazy('push notification string')
    )
    # Translators: original: url git repozitára
    url = models.CharField(
        max_length=128,
        # Translators: original: url git repozitára
        verbose_name=ugettext_lazy('git repository URL'))
    class Meta:
        # Translators: original: Repozitár
        verbose_name = ugettext_lazy('Repository')
        # Translators: original: Repozitáre
        verbose_name_plural = ugettext_lazy('Repositories')

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Competition(models.Model):
    '''
    Consists of series.
    '''
    name = models.CharField(
        max_length=128,
        # Translators: original: názov
        verbose_name=ugettext_lazy('name')
    )
    sites = models.ManyToManyField(Site)
    repo = models.ForeignKey(
        Repository, null=True, blank=True,
        # Translators: original: git repozitár
        verbose_name=ugettext_lazy('git repository')
    )
    repo_root = models.CharField(
        max_length=128,
        # Translators: original: adresa foldra súťaže v repozitári
        verbose_name=ugettext_lazy('folder path in repository')
    )
    organizers_group = models.ForeignKey(
        Group,
        null=True,
        # Translators: original: skupina vedúcich
        verbose_name=ugettext_lazy('organizers group')
    )
    primary_school_only = models.BooleanField(
        default=False,
        # Translators: original: súťaž je iba pre základoškolákov
        verbose_name=ugettext_lazy('elementary school only')
    )

    @property
    def rules(self):
        return get_rules_for_competition(self)

    objects = CompetitionManager()

    class Meta:
        # Translators: original: Súťaž
        verbose_name = ugettext_lazy('Competition')
        # Translators: original: Súťaže
        verbose_name_plural = ugettext_lazy('Competitions')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Series(models.Model):
    '''
    Series consists of several rounds.
    '''
    # Translators: original: súťaž
    competition = models.ForeignKey(Competition, verbose_name=ugettext_lazy('competition'))
    name = models.CharField(
        max_length=32,
        # Translators: original: názov
        verbose_name=ugettext_lazy('name'),
        blank=True
    )
    # Translators: original: číslo časti
    number = models.IntegerField(verbose_name=ugettext_lazy('semester number'))
    # Translators: original: ročník
    year = models.IntegerField(verbose_name=ugettext_lazy('year'))

    class Meta:
        # Translators: original: Časť
        verbose_name = ugettext_lazy('Semester')
        # Translators: original: Časti
        verbose_name_plural = ugettext_lazy('Semesters')

    def __str__(self):
        # Translators: original: %i. (%s) časť, %i. ročník %s
        return ugettext_lazy('semester: %i (%s), year %i, %s')\
            % (self.number, self.name, self.year, self.competition)

    def short_str(self):
        # Translators: original: %i. (%s) časť
        return ugettext_lazy('semester: %i (%s)')\
            % (self.number, self.name)
    # Translators: original: Časť
    short_str.short_description = ugettext_lazy('Semester')


@python_2_unicode_compatible
class Round(models.Model):
    '''
    Round has tasks.
    Holds information about deadline and such things
    '''
    # Translators: original: časť
    series = models.ForeignKey(Series, verbose_name=ugettext_lazy('semester'))
    # Translators: original: číslo
    number = models.IntegerField(verbose_name=ugettext_lazy('number'))
    start_time = models.DateTimeField(
        # Translators: original: začiatok
        verbose_name=ugettext_lazy('start time'),
        default=utils.default_start_time
    )
    end_time = models.DateTimeField(
        # Translators: original: koniec
        verbose_name=ugettext_lazy('end time'),
        default=utils.default_end_time
    )
    visible = models.BooleanField(
        # Translators: original: viditeľnosť
        verbose_name=ugettext_lazy('visible')
    )
    solutions_visible = models.BooleanField(
        # Translators: original: viditeľnosť vzorákov
        verbose_name=ugettext_lazy('visible solutions')
    )

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

    def frozen_results_exists(self, single_round=False):
        return FrozenResults.objects.filter(round=self, is_single_round=single_round).exists()

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

    @property
    def categories(self):
        return self.series.competition.category_set.all()

    class Meta:
        # Translators: original: Séria
        verbose_name = ugettext_lazy('Round')
        # Translators: original: Série
        verbose_name_plural = ugettext_lazy('Rounds')

    def __str__(self):
        # Translators: original: %i. séria, %i. časť, %i. ročník %s
        return ugettext_lazy('round: %i, semester: %i, year: %i, %s') % (
            self.number,
            self.series.number,
            self.series.year,
            self.series.competition,
        )

    def short_str(self):
        # Translators: original: %i. séria
        return ugettext_lazy('round: %i') % self.number
    # Translators: original: séria
    short_str.short_description = ugettext_lazy('round')
