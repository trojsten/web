# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from decimal import Decimal
from django.utils.safestring import mark_safe
from markdown import markdown
import os

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from trojsten.regal.contests.models import Round, Competition
from trojsten.regal.people.models import User
from trojsten.regal.people.constants import GRADUATION_SCHOOL_YEAR
from trojsten.regal.people.constants import SCHOOL_YEAR_END_MONTH
from trojsten.submit import constants as submit_constants


class TaskManager(models.Manager):
    def for_rounds_and_category(self, rounds, category=None):
        """Returns tasks which belong to specified rounds and category
        """
        if not rounds:
            return self.none()
        tasks = self.filter(
            round__in=rounds
        )
        if category is not None:
            tasks = tasks.filter(
                category=category
            )
        return tasks.order_by('round', 'number')


class SubmitManager(models.Manager):
    def for_tasks(self, tasks, include_staff=False):
        """Returns submits which belong to specified tasks.
        Only one submit per user, submit type and task is returned.
        Submits made after round.end_time are not counted except review submits,
        which has testing_status=SUBMIT_STATUS_REVIEWED and are made by organizers.
        """
        submits = self
        if not include_staff and tasks:
            # round ends January 2014 => exclude 2013, 2012,
            # round ends Jun 2014 => exclude 2013, 2012,
            # round ends September 2014 => exclude 2014, 2013,
            # round ends December 2014 => exclude 2014, 2013,
            minimal_year_of_graduation = tasks[0].round.end_time.year + int(
                tasks[0].round.end_time.month > SCHOOL_YEAR_END_MONTH
            )
            if tasks[0].round.series.competition.primary_school_only:
                minimal_year_of_graduation += GRADUATION_SCHOOL_YEAR
            submits = submits.exclude(
                user__graduation__lt=minimal_year_of_graduation
            ).exclude(
                user__in=User.objects.filter(
                    groups=tasks[0].round.series.competition.organizers_group
                )
            )

        return submits.filter(
            task__in=tasks,
        ).filter(
            models.Q(time__lte=models.F('task__round__end_time'))
            | models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        ).order_by(
            'user', 'task', 'submit_type', '-time', '-id',
        ).distinct(
            'user', 'task', 'submit_type'
        ).select_related('user__school', 'task')

    def latest_for_user(self, tasks, user):
        """Returns latest submits which belong to specified tasks and user.
        Only one submit per submit type and task is returned.
        """
        return self.filter(
            user=user,
            task__in=tasks,
        ).filter(
            models.Q(time__lte=models.F('task__round__end_time'))
            | models.Q(testing_status=submit_constants.SUBMIT_STATUS_REVIEWED)
        ).order_by(
            'task', 'submit_type', '-time', '-id',
        ).distinct(
            'task', 'submit_type'
        )


@python_2_unicode_compatible
class Category(models.Model):
    """
    Competition consists of a few categories. Each task belongs to one or more
    categories.
    """
    name = models.CharField(max_length=16, verbose_name='názov')
    competition = models.ForeignKey(Competition, verbose_name='súťaž')

    @property
    def full_name(self):
        return '%s-%s' % (self.competition.name, self.name)

    class Meta:
        verbose_name = 'Kategória'
        verbose_name_plural = 'Kategórie'

    def __str__(self):
        return self.full_name


@python_2_unicode_compatible
class Task(models.Model):
    """
    Task has its number, name, type and points value.
    Task has submits.
    """
    name = models.CharField(max_length=128, verbose_name='názov')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        verbose_name='opravovateľ',
    )
    round = models.ForeignKey(Round, verbose_name='kolo')
    category = models.ManyToManyField(Category, verbose_name='kategória', blank=True)
    number = models.IntegerField(verbose_name='číslo')
    description_points = models.IntegerField(verbose_name='body za popis')
    source_points = models.IntegerField(verbose_name='body za program')
    integer_source_points = models.BooleanField(
        default=True, verbose_name='celočíselné body za program'
    )
    has_source = models.BooleanField(verbose_name='odovzáva sa zdroják')
    has_description = models.BooleanField(verbose_name='odovzáva sa popis')
    has_testablezip = models.BooleanField(
        verbose_name='odovzdáva sa zip na testovač', default=False
    )
    external_submit_link = models.CharField(
        max_length=128, verbose_name='Odkaz na externé odovzdávanie',
        blank=True, null=True,
    )

    objects = TaskManager()

    class Meta:
        verbose_name = 'Úloha'
        verbose_name_plural = 'Úlohy'

    def __str__(self):
        return '%i. %s, %s' % (self.number, self.name, self.round)

    def has_submit_type(self, submit_type):
        check_field = {
            Submit.SOURCE: self.has_source,
            Submit.DESCRIPTION: self.has_description,
            Submit.TESTABLE_ZIP: self.has_testablezip,
            Submit.EXTERNAL: bool(self.external_submit_link),
        }
        return check_field[submit_type]

    @property
    def has_submit_list(self):
        submit_list_types = set(st for st, _ in Submit.SUBMIT_TYPES) - {Submit.EXTERNAL}
        return bool(submit_list_types & set(self.get_submit_types()))

    def get_submit_types(self):
        return [
            submit_type
            for submit_type, _ in Submit.SUBMIT_TYPES
            if self.has_submit_type(submit_type)
        ]

    def get_path(self, solution=False):
        task_file = '{}{}.html'.format(
            settings.TASK_STATEMENTS_PREFIX_TASK,
            self.number,
        )
        path = os.path.join(
            self.round.get_path(solution),
            settings.TASK_STATEMENTS_HTML_DIR,
            task_file,
        )
        return path

    def get_absolute_url(self):
        return reverse('solution_statement', kwargs={'task_id': self.id})

    @property
    def task_file_exists(self):
        path = self.get_path(solution=False)
        return os.path.exists(path)

    @property
    def solution_file_exists(self):
        path = self.get_path(solution=True)
        return os.path.exists(path)

    def visible(self, user):
        return self.round.is_visible_for_user(user)

    def solution_visible(self, user):
        return self.round.solutions_are_visible_for_user(user)


@python_2_unicode_compatible
class Submit(models.Model):
    """
    Submit holds information about its task and person who submitted it.
    There are 2 types of submits. Description submit and source submit.
    Description submit has points and filename, Source submit has also
    tester response and protocol ID assigned.
    """
    SOURCE = 0
    DESCRIPTION = 1
    TESTABLE_ZIP = 2
    EXTERNAL = 3
    SUBMIT_TYPES = [
        (SOURCE, 'source'),
        (DESCRIPTION, 'description'),
        (TESTABLE_ZIP, 'testable_zip'),
        (EXTERNAL, 'external'),
    ]
    STATUS_REVIEWED = "reviewed"
    task = models.ForeignKey(Task, verbose_name='úloha')
    time = models.DateTimeField(auto_now_add=True, verbose_name='čas')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='odovzdávateľ')
    submit_type = models.IntegerField(verbose_name='typ submitu', choices=SUBMIT_TYPES)
    points = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='body')

    filepath = models.CharField(max_length=128, verbose_name='súbor', blank=True)
    testing_status = models.CharField(
        max_length=128, verbose_name='stav testovania', blank=True)
    tester_response = models.CharField(
        max_length=10, verbose_name='odpoveď testovača', blank=True,
        help_text='Očakávané odpovede sú %s' % (', '.join(submit_constants.SUBMIT_VERBOSE_RESPONSE.keys()), )
    )
    protocol_id = models.CharField(
        max_length=128, verbose_name='číslo protokolu', blank=True)

    reviewer_comment = models.TextField(verbose_name='komentár od opravovateľa', blank=True)

    objects = SubmitManager()

    class Meta:
        verbose_name = 'Submit'
        verbose_name_plural = 'Submity'

    def __str__(self):
        return '%s - %s <%s> (%s)' % (
            self.user,
            self.task,
            Submit.SUBMIT_TYPES[self.submit_type][1],
            str(self.time),
        )

    @property
    def protocol_path(self):
        return self.filepath.rsplit('.', 1)[0] + settings.PROTOCOL_FILE_EXTENSION

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    @property
    def rendered_comment(self):
        return mark_safe(markdown(self.reviewer_comment, safe_mode=False))

    @property
    def tester_response_verbose(self):
        return submit_constants.SUBMIT_VERBOSE_RESPONSE.get(self.tester_response, self.tester_response)

    @staticmethod
    def display_decimal_value(value, is_integer):
        if is_integer:
            return value.quantize(Decimal(1))
        else:
            return value.quantize(Decimal('1.00'))

    @property
    def tested(self):
        return self.testing_status == submit_constants.SUBMIT_STATUS_FINISHED

    @property
    def user_points(self):
        """
        Returns points visible to user.
        Description points is always converted to integer.
        Source points are converted to integer if self.task.integer_source_points == True
        """
        return Submit.display_decimal_value(
            self.points,
            self.submit_type == Submit.DESCRIPTION or self.task.integer_source_points,
        )
