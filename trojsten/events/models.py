# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import mark_safe
from markdown import markdown

from trojsten.contests.models import Semester


class EventTypeManager(models.Manager):
    def current_site_only(self):
        """Returns only event types belonging to current site
        """
        return Site.objects.get_current().eventtype_set.all()


@python_2_unicode_compatible
class EventType(models.Model):
    """
    Type of event e.g. camp
    """
    name = models.CharField(max_length=100, verbose_name='názov')
    sites = models.ManyToManyField(Site, blank=True)
    organizers_group = models.ForeignKey(
        Group, verbose_name='skupina vedúcich'
    )
    is_camp = models.BooleanField(verbose_name='sústredko')

    objects = EventTypeManager()

    class Meta:
        verbose_name = 'typ akcie'
        verbose_name_plural = 'typy akcií'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Link(models.Model):
    title = models.CharField(max_length=100, verbose_name='titulok')
    name = models.CharField(max_length=300, verbose_name='meno')
    url = models.URLField(max_length=300)

    class Meta:
        verbose_name = 'odkaz'
        verbose_name_plural = 'odkazy'

    def __str__(self):
        return '%s(%s)' % (self.name, self.url)


@python_2_unicode_compatible
class EventPlace(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    address = models.ForeignKey('people.Address', null=True, blank=True)

    class Meta:
        verbose_name = 'miesto akcie'
        verbose_name_plural = 'miesta akcií'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Registration(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    text = models.TextField(help_text='Obsah bude prehnaný <a '
                                      'href="http://en.wikipedia.org/wiki/Markdown">'
                                      'Markdownom</a>.')
    required_user_properties = models.ManyToManyField(
        'people.UserPropertyKey', verbose_name='povinné údaje',
        blank=True, related_name='+',
    )

    class Meta:
        verbose_name = 'Prihláška'
        verbose_name_plural = 'Prihlášky'

    def __str__(self):
        return self.name

    @property
    def rendered_text(self):
        return mark_safe(markdown(self.text, safe_mode=False))


@python_2_unicode_compatible
class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name='názov')
    type = models.ForeignKey(EventType, verbose_name='typ akcie')
    registration = models.ForeignKey(
        Registration, null=True, blank=True, verbose_name='prihláška'
    )
    place = models.ForeignKey(EventPlace, verbose_name='miesto')
    start_time = models.DateTimeField(verbose_name='čas začiatku')
    end_time = models.DateTimeField(verbose_name='čas konca')
    registration_deadline = models.DateTimeField(
        verbose_name='deadline pre registráciu', blank=True, null=True
    )
    text = models.TextField(help_text='Obsah bude prehnaný <a '
                                      'href="http://en.wikipedia.org/wiki/Markdown">'
                                      'Markdownom</a>.', default='', blank=True)
    links = models.ManyToManyField(
        Link, blank=True, verbose_name='zoznam odkazov'
    )
    semester = models.ForeignKey(Semester, blank=True, null=True, verbose_name='semester')

    @property
    def participants(self):
        """Returns a list of EventParticipant, which are not organisers and are going to the Event."""
        return self.eventparticipant_set.filter(going=True).exclude(type=EventParticipant.ORGANIZER).select_related(
            'user')

    @property
    def organizers(self):
        """Returns a list of EventParticipant organizing the Event."""
        return self.eventparticipant_set.filter(type=EventParticipant.ORGANIZER).select_related(
            'user')

    class Meta:
        verbose_name = 'akcia'
        verbose_name_plural = 'akcie'
        ordering = ['-end_time', '-start_time']

    def __str__(self):
        return self.name

    @property
    def rendered_text(self):
        return mark_safe(markdown(self.text, safe_mode=False))


@python_2_unicode_compatible
class EventParticipant(models.Model):
    PARTICIPANT = 0
    RESERVE = 1
    ORGANIZER = 2
    TYPE_CHOICES = (
        (PARTICIPANT, 'účastník'),
        (RESERVE, 'náhradník'),
        (ORGANIZER, 'vedúci'),
    )
    event = models.ForeignKey(Event, verbose_name='akcia')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='používateľ')
    type = models.SmallIntegerField(
        choices=TYPE_CHOICES, default=PARTICIPANT, verbose_name='typ pozvania'
    )
    going = models.BooleanField(default=True, verbose_name='zúčastnil sa')

    class Meta:
        verbose_name = 'pozvánka'
        verbose_name_plural = 'pozvánky'
        unique_together = ('event', 'user')

    def __str__(self):
        return '%s(%s): %s (%s)' % (
            self.event, self.get_type_display(), self.user, self.going
        )


class EventOrganizerManager(models.Manager):
    def get_queryset(self):
        return super(EventOrganizerManager, self).get_queryset().filter(
            type=EventParticipant.ORGANIZER
        )


class EventOrganizer(EventParticipant):
    objects = EventOrganizerManager()

    class Meta:
        proxy = True
        verbose_name = 'vedúci'
        verbose_name_plural = 'vedúci'

    def save(self, *args, **kwargs):
        self.type = EventParticipant.ORGANIZER
        super(EventOrganizer, self).save(*args, **kwargs)
