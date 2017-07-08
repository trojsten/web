# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from . import constants


class UserManager(DjangoUserManager):
    def invited_to(self, event, invitation_type=None, going_only=False):
        filters = {
            'invitation__event': event
        }
        if invitation_type is not None:
            filters['invitation__type'] = invitation_type
        if going_only:
            filters['invitation__going'] = True

        return self.filter(**filters).select_related('school')


class AbstractAddress(models.Model):
    street = models.CharField(max_length=70, verbose_name='ulica')
    town = models.CharField(max_length=64, db_index=True, verbose_name='mesto')
    postal_code = models.CharField(
        max_length=16, db_index=True, verbose_name='PSČ')
    country = models.CharField(
        max_length=32, db_index=True, verbose_name='krajina')

    class Meta:
        abstract = True
        verbose_name = 'Adresa'
        verbose_name_plural = 'Adresy'


@python_2_unicode_compatible
class Address(AbstractAddress):
    def __str__(self):
        return '%s, %s, %s, %s' % (self.street, self.town, self.postal_code, self.country)


@python_2_unicode_compatible
class SchoolAddress(AbstractAddress):
    addr_name = models.CharField(max_length=100, blank=True, verbose_name='názov v adrese')
    recipient = models.CharField(max_length=100, blank=True, verbose_name='meno adresáta')

    def __str__(self):
        return '%s, %s, %s, %s' % (self.addr_name, self.street, self.town, self.postal_code)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class User(AbstractUser):
    """
    Holds, provide access to or manages all informations
    related to a person.
    """
    GENDER_CHOICES = [('M', 'Chlapec'), ('F', 'Dievča')]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        verbose_name='pohlavie',
    )
    birth_date = models.DateField(
        null=True, db_index=True, verbose_name='dátum narodenia')
    home_address = models.ForeignKey(Address,
                                     related_name='lives_here',
                                     null=True,
                                     verbose_name='domáca adresa')
    mailing_address = models.ForeignKey(Address,
                                        related_name='accepting_mails_here',
                                        blank=True,
                                        null=True,
                                        verbose_name='adresa korešpondencie')
    mail_to_school = models.BooleanField(default=False,
                                         verbose_name='posielať poštu do školy')
    school = models.ForeignKey('schools.School',
                               null=True,
                               verbose_name='škola',
                               help_text='Do políčka napíšte skratku, '
                                         'časť názvu alebo adresy školy a následne '
                                         'vyberte správnu možnosť zo zoznamu. '
                                         'Pokiaľ vaša škola nie je '
                                         'v&nbsp;zozname, vyberte "Iná škola" '
                                         'a&nbsp;pošlite nám e-mail.')
    graduation = models.IntegerField(null=True,
                                     verbose_name='rok maturity',
                                     help_text='Povinné pre žiakov.')
    ignored_competitions = models.ManyToManyField('contests.Competition',
                                                  verbose_name='ignorované súťaže')

    objects = UserManager()

    def is_in_group(self, group):
        return self.is_superuser or self.groups.filter(pk=group.pk).exists()

    def get_mailing_address(self):
        if self.mailing_address:
            return self.mailing_address
        elif self.get_mailing_option() == constants.MAILING_OPTION_SCHOOL:
            return self.get_school_mailing_address()
        return self.home_address

    def get_mailing_option(self):
        if self.mail_to_school:
            return constants.MAILING_OPTION_SCHOOL
        if self.mailing_address:
            return constants.MAILING_OPTION_OTHER
        return constants.MAILING_OPTION_HOME

    class Meta:
        verbose_name = 'používateľ'
        verbose_name_plural = 'používatelia'

    @property
    def school_year(self):
        return self.school_year_at(
            timezone.localtime(timezone.now()).date()
        )

    def school_year_at(self, date):
        current_year = date.year + int(
            date.month > constants.SCHOOL_YEAR_END_MONTH
        )
        return current_year - self.graduation + constants.GRADUATION_SCHOOL_YEAR

    def get_properties(self):
        return {prop.key: prop.value for prop in self.properties.all()}

    def get_school_mailing_address(self):
        address = self.school.get_mailing_address()
        address.recipient = '%s %s' % (self.first_name, self.last_name)
        return address

    def is_valid_for_competition(self, competition):
        required_props = competition.required_user_props.all()
        user_props = self.get_properties().keys()
        return all(map(lambda prop: prop in user_props, required_props))

    def is_competition_ignored(self, competition):
        return competition in self.ignored_competitions.all()

    def __str__(self):
        return '%s (%s)' % (self.username, self.get_full_name())

    def save(self, *args, **kwargs):
        if not self.username:
            def format_name(num):
                return unidecode("{}{}{}".format(self.first_name, self.last_name, num))

            number = 0

            while User.objects.filter(username=format_name(number)).exists():
                number += 1

            self.username = format_name(number)

        super(User, self).save(*args, **kwargs)


User._meta.get_field('first_name').blank = False
User._meta.get_field('last_name').blank = False
User._meta.get_field('username').blank = True


class UserPropertyManager(models.Manager):
    def get_queryset(self):
        return super(UserPropertyManager, self).get_queryset().select_related('key')

    def visible(self, user):
        if user.is_staff:
            return self.get_queryset()
        else:
            return self.filter(key__hidden=False)


@python_2_unicode_compatible
class UserPropertyKey(models.Model):
    """
    Type of key for additional user properties.
    """
    key_name = models.CharField(max_length=100,
                                verbose_name='názov vlastnosti')
    regex = models.CharField(
        max_length=100, verbose_name='regulárny výraz pre hodnotu', blank=True, null=True
    )
    hidden = models.BooleanField(default=False, verbose_name='skryté')

    def __str__(self):
        return self.key_name

    class Meta:
        verbose_name = 'kľúč dodatočnej vlastnosti'
        verbose_name_plural = 'kľúče dodatočnej vlastnosti'


@python_2_unicode_compatible
class UserProperty(models.Model):
    """
    Additional user properties, can be called as related_name in QuerySet of User.
    """
    user = models.ForeignKey(User,
                             related_name='properties')
    key = models.ForeignKey(UserPropertyKey,
                            verbose_name='názov vlastnosti',
                            related_name='properties')
    value = models.TextField(verbose_name='hodnota vlastnosti')

    objects = UserPropertyManager()

    def __str__(self):
        return '%s: %s' % (self.key, self.value)

    class Meta:
        verbose_name = 'dodatočná vlastnosť'
        verbose_name_plural = 'dodatočné vlastnosti'
        unique_together = ('user', 'key')

    def clean(self):
        if self.key.regex and not re.match(self.key.regex, self.value):
            raise ValidationError(
                _('Value "{}" does not match regex "{}".').format(self.value, self.key.regex)
            )


@python_2_unicode_compatible
class DuplicateUser(models.Model):
    """
    Merge candidate users - users with duplicit name or other properties.
    """
    MERGE_STATUS_UNRESOLVED = 0
    MERGE_STATUS_NOT_DUPOLICATE = 1
    MERGE_STATUS_RESOLVED = 2
    MERGE_STATUS_CHOICES = [
        (MERGE_STATUS_UNRESOLVED, 'Nevyriešené'),
        (MERGE_STATUS_NOT_DUPOLICATE, 'Nie je duplikát'),
        (MERGE_STATUS_RESOLVED, 'Vyriešený duplikát'),
    ]
    user = models.OneToOneField(User)
    status = models.IntegerField(
        choices=MERGE_STATUS_CHOICES,
        default=0,
        verbose_name='stav',
    )

    def __str__(self):
        return '%s' % (self.user,)

    class Meta:
        verbose_name = 'duplicitný používateľ'
        verbose_name_plural = 'duplicitní používatelia'
