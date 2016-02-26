# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager

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


@python_2_unicode_compatible
class Address(models.Model):
    street = models.CharField(max_length=70, verbose_name='ulica')
    town = models.CharField(max_length=64, db_index=True, verbose_name='mesto')
    postal_code = models.CharField(
        max_length=16, db_index=True, verbose_name='PSČ')
    country = models.CharField(
        max_length=32, db_index=True, verbose_name='krajina')

    def __str__(self):
        return '%s, %s, %s, %s' % (self.street, self.town, self.postal_code, self.country)

    class Meta:
        verbose_name = 'Adresa'
        verbose_name_plural = 'Adresy'


@python_2_unicode_compatible
class School(models.Model):
    abbreviation = models.CharField(max_length=100,
                                    blank=True,
                                    verbose_name='skratka',
                                    help_text='Sktatka názvu školy.')
    verbose_name = models.CharField(max_length=100,
                                    verbose_name='celý názov')
    addr_name = models.CharField(max_length=100, blank=True, verbose_name='názov v adrese')
    street = models.CharField(max_length=100, blank=True, verbose_name='ulica')
    city = models.CharField(max_length=100, blank=True, verbose_name='mesto')
    zip_code = models.CharField(max_length=10, blank=True, verbose_name='PSČ')

    class Meta:
        verbose_name = 'škola'
        verbose_name_plural = 'školy'
        ordering = ('city', 'street', 'verbose_name')

    def __str__(self):
        result = ''
        if self.abbreviation:
            result += self.abbreviation + ', '
        result += self.verbose_name
        if self.street:
            result += ', ' + self.street
        if self.city or self.zip_code:
            result += ', '
        if self.zip_code:
            result += self.zip_code
        if self.city:
            result += ' ' + self.city
        return result

    @property
    def has_abbreviation(self):
        return self.abbreviation.strip() != ''


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
    school = models.ForeignKey(School,
                               null=True,
                               default=1,
                               verbose_name='škola',
                               help_text='Do políčka napíšte skratku, '
                               'časť názvu alebo adresy školy a následne '
                               'vyberte správnu možnosť zo zoznamu. '
                               'Pokiaľ vaša škola nie je '
                               'v&nbsp;zozname, vyberte "Gymnázium iné" '
                               'a&nbsp;pošlite nám e-mail.')
    graduation = models.IntegerField(null=True,
                                     verbose_name='rok maturity',
                                     help_text='Povinné pre žiakov.')

    objects = UserManager()

    def is_in_group(self, group):
        return self.is_superuser or self.groups.filter(pk=group.pk).exists()

    def get_mailing_address(self):
        return self.home_address if self.mailing_address is None else self.mailing_address

    class Meta:
        verbose_name = 'používateľ'
        verbose_name_plural = 'používatelia'

    @property
    def school_year(self):
        current_year = date.today().year + int(
            date.today().month > constants.SCHOOL_YEAR_END_MONTH
        )
        return current_year - self.graduation + constants.GRADUATION_SCHOOL_YEAR

    def __str__(self):
        return '%s (%s)' % (self.username, self.get_full_name())


@python_2_unicode_compatible
class UserPropertyKey(models.Model):
    """
    Type of key for additional user properties.
    """
    key_name = models.CharField(max_length=100,
                                verbose_name='názov vlastnosti')

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

    def __str__(self):
        return '%s: %s' % (self.key, self.value)

    class Meta:
        verbose_name = 'dodatočná vlastnosť'
        verbose_name_plural = 'dodatočné vlastnosti'
        unique_together = ('user', 'key')


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
        return '%s: %s' % (self.user, self.status)

    class Meta:
        verbose_name = 'duplicitný používateľ'
        verbose_name_plural = 'duplicitní používatelia'
