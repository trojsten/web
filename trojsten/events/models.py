# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db import models
from django.utils.html import mark_safe
from markdown import markdown

from trojsten.contests.models import Semester


class EventTypeManager(models.Manager):
    def current_site_only(self):
        """Returns only event types belonging to current site
        """
        return Site.objects.get_current().eventtype_set.all()


class EventType(models.Model):
    """
    Type of event e.g. camp
    """

    name = models.CharField(max_length=100, verbose_name="názov")
    sites = models.ManyToManyField(Site, blank=True)
    organizers_group = models.ForeignKey(
        Group, verbose_name="skupina vedúcich", on_delete=models.CASCADE
    )
    is_camp = models.BooleanField(verbose_name="sústredko")

    objects = EventTypeManager()

    class Meta:
        verbose_name = "typ akcie"
        verbose_name_plural = "typy akcií"

    def __str__(self):
        return self.name


class EventPlace(models.Model):
    name = models.CharField(max_length=100, verbose_name="názov")
    address = models.ForeignKey("people.Address", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "miesto akcie"
        verbose_name_plural = "miesta akcií"

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=100, verbose_name="názov")
    type = models.ForeignKey(EventType, verbose_name="typ akcie", on_delete=models.CASCADE)
    place = models.ForeignKey(EventPlace, verbose_name="miesto", on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name="čas začiatku")
    end_time = models.DateTimeField(verbose_name="čas konca")
    text = models.TextField(
        help_text="Obsah bude prehnaný <a "
        'href="http://en.wikipedia.org/wiki/Markdown">'
        "Markdownom</a>.",
        default="",
        blank=True,
    )
    semester = models.ForeignKey(
        Semester, blank=True, null=True, verbose_name="semester", on_delete=models.CASCADE
    )

    @property
    def participants(self):
        """Returns a list of EventParticipant, which are not organisers and are going to the Event.
        """
        return (
            self.eventparticipant_set.filter(going=True)
            .exclude(type=EventParticipant.ORGANIZER)
            .select_related("user")
        )

    @property
    def organizers(self):
        """Returns a list of EventParticipant organizing the Event."""
        return self.eventparticipant_set.filter(type=EventParticipant.ORGANIZER).select_related(
            "user"
        )

    class Meta:
        verbose_name = "akcia"
        verbose_name_plural = "akcie"
        ordering = ["-end_time", "-start_time"]

    def __str__(self):
        return self.name

    @property
    def rendered_text(self):
        return mark_safe(markdown(self.text, safe_mode=False))


class EventParticipant(models.Model):
    PARTICIPANT = 0
    RESERVE = 1
    ORGANIZER = 2
    TYPE_CHOICES = ((PARTICIPANT, "účastník"), (RESERVE, "náhradník"), (ORGANIZER, "vedúci"))
    event = models.ForeignKey(Event, verbose_name="akcia", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="používateľ", on_delete=models.CASCADE
    )
    type = models.SmallIntegerField(
        choices=TYPE_CHOICES, default=PARTICIPANT, verbose_name="typ pozvania"
    )
    going = models.BooleanField(default=True, verbose_name="zúčastnil sa")

    class Meta:
        verbose_name = "účastník akcie"
        verbose_name_plural = "účastníci akcie"
        unique_together = ("event", "user")

    def __str__(self):
        return "%s(%s): %s (%s)" % (self.event, self.get_type_display(), self.user, self.going)


class EventOrganizerManager(models.Manager):
    def get_queryset(self):
        return (
            super(EventOrganizerManager, self)
            .get_queryset()
            .filter(type=EventParticipant.ORGANIZER)
        )


class EventOrganizer(EventParticipant):
    objects = EventOrganizerManager()

    class Meta:
        proxy = True
        verbose_name = "vedúci akcie"
        verbose_name_plural = "vedúci akcie"

    def save(self, *args, **kwargs):
        self.type = EventParticipant.ORGANIZER
        self.going = True
        super(EventOrganizer, self).save(*args, **kwargs)
