# -*- coding: utf-8 -*-

import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from unidecode import unidecode

from trojsten.people.models import User, UserPropertyKey
from trojsten.results.models import FrozenResults
from trojsten.rules import get_rules_for_competition
from trojsten.rules.susi_constants import (
    SUSI_BIG_HINT_DAYS,
    SUSI_COMPETITION_ID,
    SUSI_OUTDOOR_ROUND_NUMBER,
)
from trojsten.submit import constants as submit_constants
from trojsten.utils import utils

from . import constants


class CompetitionManager(models.Manager):
    def current_site_only(self):
        """Returns only competitions belonging to current site"""
        return Competition.objects.filter(sites__id=settings.SITE_ID).order_by("pk").all()


class Competition(models.Model):
    """
    Consists of semester.
    """

    name = models.CharField(max_length=128, verbose_name="názov")
    sites = models.ManyToManyField(Site)
    organizers_group = models.ForeignKey(
        Group, null=True, verbose_name="skupina vedúcich", on_delete=models.CASCADE
    )
    primary_school_only = models.BooleanField(
        default=False, verbose_name="súťaž je iba pre základoškolákov"
    )
    required_user_props = models.ManyToManyField(
        UserPropertyKey,
        limit_choices_to={"hidden": False},
        verbose_name="Povinné vlastnosti človeka",
        blank=True,
    )

    @property
    def rules(self):
        return get_rules_for_competition(self)

    objects = CompetitionManager()

    class Meta:
        verbose_name = "Súťaž"
        verbose_name_plural = "Súťaže"

    def __str__(self):
        return self.name


class SemesterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("competition")


class Semester(models.Model):
    """
    Semester consists of several rounds.
    """

    competition = models.ForeignKey(Competition, verbose_name="súťaž", on_delete=models.CASCADE)
    name = models.CharField(max_length=32, verbose_name="názov", blank=True)
    number = models.IntegerField(verbose_name="číslo části")
    year = models.IntegerField(verbose_name="ročník")

    objects = SemesterManager()

    class Meta:
        verbose_name = "Časť"
        verbose_name_plural = "Časti"

    @property
    def start_time(self):
        return self.round_set.order_by("start_time")[0].start_time

    @property
    def end_time(self):
        """
        Adding new rounds to a semester alters this property, thus it should only be used with
        semesters that have already ended unless accounted for.
        """
        return self.round_set.order_by("-end_time")[0].end_time

    def __str__(self):
        # All foreign keys here should be added to the select_related list in the RoundManager.
        return "%i. (%s) časť, %i. ročník %s" % (
            self.number,
            self.name,
            self.year,
            self.competition,
        )

    def short_str(self):
        return "%i. (%s) časť" % (self.number, self.name)

    short_str.short_description = "Časť"


class RoundManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("semester__competition")

    def visible(self, user, all_sites=False):
        """Returns only rounds visible for user"""
        if all_sites:
            competitions = Competition.objects.all()
        else:
            competitions = Competition.objects.current_site_only()

        res = self.filter(semester__competition__in=competitions)
        if not user.is_superuser:
            res = res.filter(
                Q(semester__competition__organizers_group__in=user.groups.all()) | Q(visible=True)
            )
        return res

    # @FIXME(unused): Was used only by actual results, moved to Rules.
    def latest_visible(self, user, all_sites=False):
        """Returns latest visible round for each competition"""
        return (
            self.visible(user, all_sites)
            .order_by("semester__competition", "-end_time", "-number")
            .distinct("semester__competition")
            .select_related("semester__competition")
        )

    def active_visible(self, user, all_sites=False):
        """Returns all visible running rounds for each competition"""
        return (
            self.visible(user, all_sites)
            .filter(
                (Q(second_end_time__isnull=False) & Q(second_end_time__gte=timezone.now()))
                | (Q(second_end_time__isnull=True) & Q(end_time__gte=timezone.now()))
            )
            .order_by("-end_time", "-number")
            .select_related("semester__competition")
        )

    def latest_finished_for_competition(self, competition):
        return (
            self.filter(
                semester__competition=competition, visible=True, end_time__lt=timezone.now()
            )
            .order_by("-end_time")
            .first()
        )


class Round(models.Model):
    """
    Round has tasks.
    Holds information about deadline and such things
    """

    semester = models.ForeignKey(Semester, verbose_name="časť", on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name="číslo")
    start_time = models.DateTimeField(verbose_name="začiatok", default=utils.default_start_time)
    end_time = models.DateTimeField(verbose_name="koniec", default=utils.default_end_time)
    second_end_time = models.DateTimeField(
        verbose_name="druhý koniec", blank=True, null=True, default=None
    )
    visible = models.BooleanField(verbose_name="viditeľnosť", default=False)
    solutions_visible = models.BooleanField(verbose_name="viditeľnosť vzorákov", default=False)
    results_final = models.BooleanField(verbose_name="výsledky sú finálne", default=False)

    objects = RoundManager()

    @property
    def number_str(self):
        if self.susi_is_outdoor:
            return "Outdoor"
        else:
            return "%i." % self.number

    @property
    def can_submit(self):
        end = self.end_time if self.second_end_time is None else self.second_end_time
        if timezone.now() <= end:
            return True
        return False

    @property
    def second_phase_running(self):
        return (
            self.second_end_time is not None
            and self.end_time < timezone.now() < self.second_end_time
        )

    @property
    def susi_is_outdoor(self):
        return (
            self.number == SUSI_OUTDOOR_ROUND_NUMBER
            and self.semester.competition.id == SUSI_COMPETITION_ID
        )

    @property
    def susi_big_hint_date(self):
        return self.end_time + timedelta(days=SUSI_BIG_HINT_DAYS)

    @property
    def susi_small_hint_public(self):
        return timezone.now() > self.end_time

    @property
    def susi_big_hint_public(self):
        return timezone.now() > self.susi_big_hint_date

    def get_base_path(self):
        round_dir = str(self.number)
        semester_dir = str(self.semester.number)
        year_dir = str(self.semester.year)
        competition_name = self.semester.competition.name
        path = os.path.join(competition_name, year_dir, semester_dir, round_dir)
        return path

    def get_path(self, solution=False):
        path_type = (
            settings.TASK_STATEMENTS_SOLUTIONS_DIR
            if solution
            else settings.TASK_STATEMENTS_TASKS_DIR
        )
        path = os.path.join(self.get_base_path(), path_type)
        return path

    def get_pdf_path(self, solution=False):
        pdf_file = (
            settings.TASK_STATEMENTS_SOLUTIONS_PDF if solution else settings.TASK_STATEMENTS_PDF
        )
        path = os.path.join(self.get_path(solution), pdf_file)
        return path

    def get_pictures_path(self):
        path = os.path.join(self.get_base_path(), settings.TASK_STATEMENTS_PICTURES_DIR)
        return path

    @property
    def tasks_pdf_exists(self):
        path = self.get_pdf_path(solution=False)
        return settings.TASK_STATEMENTS_STORAGE.exists(path)

    @property
    def solutions_pdf_exists(self):
        path = self.get_pdf_path(solution=True)
        return settings.TASK_STATEMENTS_STORAGE.exists(path)

    def frozen_results_exists(self, single_round=False):
        return FrozenResults.objects.filter(round=self, is_single_round=single_round).exists()

    def is_visible_for_user(self, user):
        return (
            user.is_superuser
            or self.semester.competition.organizers_group in user.groups.all()
            or self.visible
        )

    def solutions_are_visible_for_user(self, user):
        return (
            user.is_superuser
            or self.semester.competition.organizers_group in user.groups.all()
            or self.solutions_visible
        )

    @property
    def categories(self):
        return self.semester.competition.category_set.all()

    class Meta:
        verbose_name = "Kolo"
        verbose_name_plural = "Kolá"

    def __str__(self):
        # All foreign keys here should be added to the select_related list in the RoundManager.
        return self.number_str + " kolo, %i. časť, %i. ročník %s" % (
            self.semester.number,
            self.semester.year,
            self.semester.competition,
        )

    def short_str(self):
        return self.number_str + " kolo"

    short_str.short_description = "kolo"

    def get_pdf_name(self, solution=False):
        return "%s-%s%i-%s%i-%s.pdf" % (
            self.semester.competition,
            unidecode(_("year")),
            self.semester.year,
            unidecode(_("round")),
            self.number,
            unidecode(_("solutions")) if solution else unidecode(_("tasks")),
        )

    def __init__(self, *args, **kwargs):
        super(Round, self).__init__(*args, **kwargs)
        self.previous_visible = self.visible

    def save(self, *args, **kwargs):
        super(Round, self).save(*args, **kwargs)
        self.previous_visible = self.visible


class TaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("round__semester__competition")

    def for_rounds_and_category(self, rounds, category=None):
        """Returns tasks which belong to specified rounds and category"""
        if not rounds:
            return self.none()
        tasks = self.filter(round__in=rounds)
        if category is not None:
            tasks = tasks.filter(category=category)
        return tasks.order_by("round", "number")


class Category(models.Model):
    """
    Competition consists of a few categories. Each task belongs to one or more
    categories.
    """

    name = models.CharField(max_length=16, verbose_name="názov")
    competition = models.ForeignKey(Competition, verbose_name="súťaž", on_delete=models.CASCADE)

    @property
    def full_name(self):
        return "%s-%s" % (self.competition.name, self.name)

    class Meta:
        verbose_name = "Kategória"
        verbose_name_plural = "Kategórie"

    def __str__(self):
        return self.full_name


class Task(models.Model):
    """
    Task has its number, name, type and points value.
    Task has submits.
    """

    name = models.CharField(max_length=128, verbose_name="názov")
    round = models.ForeignKey(Round, verbose_name="kolo", on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, verbose_name="kategória", blank=True)
    number = models.IntegerField(verbose_name="číslo")
    description_points = models.IntegerField(verbose_name="body za popis", default=0)
    source_points = models.IntegerField(verbose_name="body za program", default=0)
    integer_source_points = models.BooleanField(
        default=True, verbose_name="celočíselné body za program"
    )
    has_source = models.BooleanField(verbose_name="odovzdáva sa zdroják", default=False)
    has_description = models.BooleanField(verbose_name="odovzdáva sa popis", default=False)
    has_testablezip = models.BooleanField(
        verbose_name="odovzdáva sa zip na testovač", default=False
    )
    external_submit_link = models.CharField(
        max_length=128, verbose_name="Odkaz na externé odovzdávanie", blank=True, null=True
    )
    text_submit_solution = ArrayField(
        models.CharField(
            max_length=512,
            verbose_name="textové riešenia (oddeľ čiarkou)",
            blank=True,
            default="",
        ),
        blank=True,
        null=False,
        default=list,
    )
    susi_small_hint = models.TextField(verbose_name="Suši malý hint", blank=True, default="")
    susi_big_hint = models.TextField(verbose_name="Suši velký hint", blank=True, default="")
    email_on_desc_submit = models.BooleanField(
        verbose_name=_("Send notification to reviewers about new description submit"), default=False
    )
    email_on_code_submit = models.BooleanField(
        verbose_name=_("Send notification to reviewers about new code submit"), default=False
    )
    description_points_visible = models.BooleanField(
        verbose_name=_("Show description points"), default=False
    )

    objects = TaskManager()

    class Meta:
        verbose_name = "Úloha"
        verbose_name_plural = "Úlohy"

    def __str__(self):
        # All (transitive) foreign keys here should be also added
        # to the select_related list in the TaskManager.
        return "%i. %s, %s" % (self.number, self.name, self.round)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.last_saved_description_points_visible = self.description_points_visible

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        self.last_saved_description_points_visible = self.description_points_visible

    @property
    def has_text_submit(self):
        return len(self.text_submit_solution) > 0

    def has_submit_type(self, submit_type):
        check_field = {
            submit_constants.SUBMIT_TYPE_SOURCE: self.has_source,
            submit_constants.SUBMIT_TYPE_DESCRIPTION: self.has_description,
            submit_constants.SUBMIT_TYPE_TESTABLE_ZIP: self.has_testablezip,
            submit_constants.SUBMIT_TYPE_EXTERNAL: bool(self.external_submit_link),
            submit_constants.SUBMIT_TYPE_TEXT: self.has_text_submit,
        }
        return check_field[submit_type]

    @property
    def has_submit_list(self):
        submit_list_types = set(st for st, _ in submit_constants.SUBMIT_TYPES) - {
            submit_constants.SUBMIT_TYPE_EXTERNAL
        }
        return bool(submit_list_types & set(self.get_submit_types()))

    def get_submit_types(self):
        return [
            submit_type
            for submit_type, _ in submit_constants.SUBMIT_TYPES
            if self.has_submit_type(submit_type)
        ]

    def get_path(self, solution=False):
        task_file = "{}{}.html".format(settings.TASK_STATEMENTS_PREFIX_TASK, self.number)
        path = os.path.join(
            self.round.get_path(solution), settings.TASK_STATEMENTS_HTML_DIR, task_file
        )
        return path

    def get_absolute_url(self):
        return reverse("solution_statement", kwargs={"task_id": self.id})

    @property
    def task_file_exists(self):
        path = self.get_path(solution=False)
        return settings.TASK_STATEMENTS_STORAGE.exists(path)

    @property
    def solution_file_exists(self):
        path = self.get_path(solution=True)
        return settings.TASK_STATEMENTS_STORAGE.exists(path)

    def visible(self, user):
        return self.round.is_visible_for_user(user)

    def solution_visible(self, user):
        return self.round.solutions_are_visible_for_user(user)

    def assign_person(self, user, role):
        TaskPeople.objects.create(task=self, user=user, role=role)

    def get_assigned_people_for_role(self, role):
        return [line.user for line in TaskPeople.objects.filter(task=self, role=role)]


class TaskPeople(models.Model):
    task = models.ForeignKey(
        Task, verbose_name=_("task"), related_name="task_people", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, verbose_name=_("organizer"), on_delete=models.CASCADE)
    TASK_ROLE_CHOICES = [
        (constants.TASK_ROLE_REVIEWER, _("reviewer")),
        (constants.TASK_ROLE_SOLUTION_WRITER, _("solution writer")),
        (constants.TASK_ROLE_PROOFREADER, _("proofreader")),
    ]
    role = models.IntegerField(choices=TASK_ROLE_CHOICES, verbose_name=_("role"))

    class Meta:
        verbose_name = _("Assigned user")
        verbose_name_plural = _("Assigned people")
