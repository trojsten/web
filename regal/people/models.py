# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from regal.properties import PropsManager


class Address(models.Model):
    street = models.CharField(max_length=64, verbose_name='ulica')
    number = models.CharField(max_length=16, verbose_name='číslo')
    town = models.CharField(max_length=64, db_index=True, verbose_name='mesto')
    postal_code = models.CharField(max_length=16, db_index=True, verbose_name='PSČ')
    country = models.CharField(max_length=32,  db_index=True, verbose_name='krajina')
    # schools_here <- related name to School.address
    # lives_here <- related name to Person.home_address
    # accepting_mails_here <- related name to Student.correspondence_address

    def __unicode__(self):
        return (
            self.street + " " + self.number + ", " +
            self.town + ", " + self.postal_code + ", " +
            self.country)

    class Meta:
        verbose_name = 'Adresa'
        verbose_name_plural = 'Adresy'


class Person(models.Model):

    """ Holds, provide access to or manages all informations
        related to a person.
    """
    name = models.CharField(
        max_length=128,  db_index=True, verbose_name='meno')
    surname = models.CharField(
        max_length=128,  db_index=True, verbose_name='priezvisko')
    birth_date = models.DateField(
        db_index=True, verbose_name='dátum narodenia')
    home_address = models.ForeignKey(Address,
            related_name='lives_here', null=True, verbose_name='domáca adresa')
    correspondence_address = models.ForeignKey(Address,
            related_name='accepting_mails_here', null=True, verbose_name='adresa korešpondencie')
    email = models.EmailField(verbose_name='e-mail')
    # studies_as <- related name to Student.person
    # studies_in <- related name to School.studying_persons
    # teaches_as <- related name to Teacher.person
    # teaches_in <- related name to School.teaching_persons

    class Meta:
        verbose_name = 'Osoba'
        verbose_name_plural = 'Ľudia'

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.props = PropsManager(self, PersonProperty)

    def study(self):
        """ Returns actual student relationship for this person
            Actual student is a student, who has NULL/None end_date
            Throws django.core.exceptions.MultipleObjectsReturned
            if there are multiple actual studnets.
        """
        try:
            r = self.studies_as.get(end_date__isnull=True)
            return r
        except ObjectDoesNotExist:
            return None

    def terminate_studies(self):
        """ Termintes all actual student relationships for this person
            Actual student is a student, who has NULL/None end_date
        """
        now = date.today()
        for act_student in list(self.studies_as.filter(end_date__isnull=True)):
            act_student.end_date = now
            if act_student.start_date == now:
                # act_student won't be interesting for the future
                act_student.delete()
                continue
            act_student.save()

    def change_study(self, school, study_type, grade=1):
        """ Terminates all actual students relationships
            and creates a new one from given school, study_type and grade
            Preffered way to create a new Student record.
            Returns created Student object.
        """
        self.terminate_studies()
        s = Student(
            school=school, person=self, study_type=study_type,
            start_date=date.today(), end_date=None)
        s.set_grade(grade)
        s.pk = None
        s.save()
        return s

    def __unicode__(self):
        return self.name + " " + self.surname


class PersonPropertyCategory(models.Model):

    """ PersonPropertyTypes can be categorized for better UI organization. """
    name = models.CharField(
        max_length=128,  db_index=True, verbose_name='meno')
    # types <- related name to PersonPropertyType.category


class PersonPropertyType(models.Model):

    """ Describes one possible type additional person properties """
    name = models.CharField(
        max_length=128,  db_index=True, verbose_name='meno')
    validity_regex = models.TextField(
        null=False, default="", verbose_name='validačný regex')
    multi = models.BooleanField(default=False, verbose_name='multi')
    category = models.ForeignKey(
        PersonPropertyCategory, related_name='types', verbose_name='kategória')
    user_editable = models.BooleanField(
        default=True, verbose_name='editovateľné užívateľom')
    user_readable = models.BooleanField(
        default=True, verbose_name='čitateľné užívateľom')
    # records <- related name to PersonProperty.type


class PersonProperty(models.Model):

    """ Every adittional property of every person is stored as this. """
    type = models.ForeignKey(PersonPropertyType,
                             related_name='records', verbose_name='typ')
    object = models.ForeignKey(
        Person, related_name='+', verbose_name='objekt')
    value = models.TextField(
        null=False, default="",  db_index=True, verbose_name='hodnota')


class School(models.Model):

    """ Holds, provide access to or manages all informations
        related to a school.
    """
    name = models.CharField(max_length=128, verbose_name='meno')
    abbr = models.CharField(max_length=16, verbose_name='skratka')
        # Used when full name is too long (e.g. results, list of participants)
    address = models.ForeignKey(Address, related_name='schools_here',
                                null=True, verbose_name='adresa')
    email = models.EmailField(null=True, verbose_name='e-mail')
    studying_persons = models.ManyToManyField(
        Person,
        through='Student',
        related_name='studies_in',
        verbose_name='študenti')
    teaching_persons = models.ManyToManyField(
        Person,
        through='Teacher',
        related_name='teaches_in',
        verbose_name='učitelia')
    # students <- related name to Student.school
    # teachers <- related name to Teacher.school

    class Meta:
        verbose_name = 'Škola'
        verbose_name_plural = 'Školy'

    def __unicode__(self):
        return self.name

    def get_town(self):
        return self.address.town

# TODO toto musi sysel opravit, lebo to cele nefunguje ##
#
'''
class StudyType(object):
    """ Set of informations about study type.
        Also defines all study types.
    """

    def __init__(self, name, abbr, grade_to_absolute):
        self.name = name
        self.abbr = abbr
        self.grade_to_absolute = grade_to_absolute
        self.max_grade = len(grade_to_absolute)-1

# Didn't work inside StudyType definition
StudyType.ZS = StudyType('Základná škola', 'ZS', [None] + range(1,10))
StudyType.SS = StudyType('Stredná škola', 'SS', [None] + range(10,14))
StudyType.VS = StudyType('Vysoká škola', 'SS', [None] + range(14,19))
StudyType.G8 = StudyType('8-ročné gymnázium', 'G8', [None] + range(6,14))
StudyType.BL = StudyType('Bilingválne gymnázium', 'BL', [None, 10] + range(10,14))


class StudyTypeField(models.CharField):
    """ Converts StudyType-s between python and database."""

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        kwargs['null'] = False
        super(StudyTypeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, StudyType):
            return value
        return getattr(StudyType, 'ZS')

    def get_prep_value(self, value):
         return value.abbr
'''


class Student(models.Model):

    """ A relationship between School and Person studying there.
        Holds and manges informations about relationship duration,
        study type, and student's grade.
        Should be able to give information about part of person's studies.
    """
    STUDY_TYPE_CHOICES = (
        ('ZS', 'Základná škola'),
        ('SS', 'Stredná škola'),
        ('VS', 'Vysoká škola'),
        ('G8', '8-ročné gymnázium'),
        ('BL', 'Bilingválne gymnázium'),
    )

    school = models.ForeignKey(
        School, related_name='students', verbose_name='škola')
    person = models.ForeignKey(
        Person, related_name='studies_as', verbose_name='osoba')
    # syslove nefunkcne:
    # study_type = StudyTypeField(default = StudyType.ZS, null=False, db_index=True)
    study_type = models.CharField(
        max_length=2, choices=STUDY_TYPE_CHOICES, default='SS', verbose_name='typ štúdia')
    start_date = models.DateField(verbose_name='začiatok štúdia')
        # Begining date of this relationship
        # Used to determine actual school in specified time
    end_date = models.DateField(null=True, verbose_name='koniec štúdia')
        # Termination date of this relationship
        # Used to determine actual school in specified time
        # None/NULL when this is actual relationship
    expected_end_year = models.SmallIntegerField(
        default=None, null=True, verbose_name='očakávaný rok skončenia')
        # The year when full study would terimnate
        # Used to determine actual grade

    class Meta:
        verbose_name = 'Študent'
        verbose_name_plural = 'Študenti'

    def is_actual():
        return end_date == None

    def get_grade(self, act_date=None):
        """ Returns actual grade calculated from expected_end_year
            You can simulate another date by optional argument "act_date".
        """
        if act_date == None:
            act_date = date.today()
        act_year = Student.date_to_school_year(act_date)
        return act_year + self.study_type.max_grade - self.expected_end_year

    def set_grade(self, grade, act_date=None):
        """ Sets expected_end_year so that actual grade will change to given
            You can simulate another date by optional argument "act_date".
        """
        if act_date == None:
            act_date = date.today()
        act_year = Student.date_to_school_year(act_date)
        self.expected_end_year = act_year + self.study_type.max_grade - grade

    def get_absolute_grade(self, act_date=None):
        return self.study_type.grade_to_absolute[self.get_grade(act_date)]

    @staticmethod
    def date_to_school_year(date_):
        """ Returns a second year of a school year of given date. """
        if date_.month > 8:
            return date_.year + 1
        else:
            return date_.year


class Teacher(models.Model):

    """ An actual relationship between school and person teaching there.
        Also stores information about teached subjects.
    """
    school = models.ForeignKey(
        School, related_name='teachers', verbose_name='škola')
    person = models.ForeignKey(
        Person, related_name='teaches_as', verbose_name='osoba')
    teaches_math = models.NullBooleanField(verbose_name='učí matematik')
    teaches_physics = models.NullBooleanField(verbose_name='učí fyzik')
    teaches_informatics = models.NullBooleanField(
        verbose_name='učí informatik')

    class Meta:
        verbose_name = 'Učiteľ'
        verbose_name_plural = 'Učitelia'
