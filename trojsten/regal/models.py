# -*- coding: utf-8 -*- 

from django.db import models
from datetime import date
from django.core.exceptions import ObjectDoesNotExist

class Address(models.Model):
    street = models.CharField(max_length=64)
    number = models.CharField(max_length=16)
    town = models.CharField(max_length=64)
    postal_code = models.CharField(max_length=16)
    country = models.CharField(max_length=32)
    
    def __unicode__(self):
        return (
            self.street + " " + self.number + ", " +
            self.town + ", " + self.postal_code + ", " +
            self.country)


class Person(models.Model):
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    birth_date = models.DateField()
    
    def __unicode__(self):
        return self.name + " " + self.surname

        
class School(models.Model):
    name = models.CharField(max_length=128)
    abbr = models.CharField(max_length=16, primary_key=True)
        # used instead of id
        # used when full name is too long (e.g. results, list of participants)
        # note: primary_key=True implies null=False and unique=True
    address = models.ForeignKey(Address, related_name='schools_here')
    studying_persons = models.ManyToManyField(
        Person,
        through='Student',
        related_name='studies_in')
    teaching_persons = models.ManyToManyField(
        Person,
        through='Teacher',
        related_name='teaches_in')
    
    def __unicode__(self):
        return self.name
    

class Student(models.Model):
    """ A relationship between School and Person.
        
    """
    school = models.ForeignKey(School, related_name='students')
    person = models.ForeignKey(Person, related_name='studies_as')
    
    

class Teacher(models.Model):
    """ A relationship between School and Person.
    """
    school = models.ForeignKey(School, related_name='teachers')
    person = models.ForeignKey(Person, related_name='teaches_as')

        


''' NIECO MU VADI, FAKT NEVIEM CO:

##############################
#    PERSONAL INFORMATIONS   #
##############################
# TODO(sysel) person propesties


class Address(models.Model):
    id = models.IntegerField(primary_key=True)
    street = models.CharField(max_length=64)
    number = models.CharField(max_length=16)
    town = models.CharField(max_length=64)
    postal_code = models.CharField(max_length=16)
    country = models.CharField(max_length=32)
    # schools_here <- related name to School.address
    # lives_here <- related name to Person.home_address
    # accepting_mails_here <- related name to Student.correspondence_address
    
    def __unicode__(self):
        return (
            self.street + " " + self.number + ", " +
            self.town + ", " + self.postal_code + ", " +
            self.country)


class Person(models.Model):
    """ Holds, provide access to or manages all informations
        related to a person.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    birth_date = models.DateField()
    home_address = models.ForeignKey(Address, related_name='lives_here')
    correspondence_address = models.ForeignKey(Address, related_name='accepting_mails_here')
    email = models.EmailField()
    # studies_as <- related name to Student.person
    # studies_in <- related name to School.studying_persons
    # teaches_as <- related name to Teacher.person
    # teaches_in <- related name to School.teaching_persons
    
    def actual_student(self, act_date=None):
        # TODO docstring
        if act_date == None:
            act_date = date.now()
        try:
            r = self.studies_as.get(end_date = None)
            return r
        except ObjectDoesNotExist:
            return None
         
    def close_actual_student(self):
        # TODO docstring
        act_student = self.actual_student()
        if act_student == None:
            return
        act_student.end_date = date.now()
        act_student.save()
    
    def __unicode__(self):
        return self.name + " " + self.surname
        
    
        
class School(models.Model):
    """ Holds, provide access to or manages all informations
        related to a school.
    """
    name = models.CharField(max_length=128)
    abbr = models.CharField(max_length=16, primary_key=True)
        # Used instead of id
        # Used when full name is too long (e.g. results, list of participants)
        # Note: primary_key=True implies null=False and unique=True
    address = models.ForeignKey(Address, related_name='schools_here')
    studying_persons = models.ManyToManyField(
        Person,
        through='Student',
        related_name='studies_in')
    teaching_persons = models.ManyToManyField(
        Person,
        through='Teacher',
        related_name='teaches_in')
    # students <- related name to Student.school
    # teachers <- related name to Teacher.school
    
    def __unicode__(self):
        return self.name
    


class Student(models.Model):
    """ A relationship between School and Person studying there.
        Holds and manges informations about relationship duration,
        study type, and student's grade.
        Should be able to give information about part of person's studies.
    """
    school = models.ForeignKey(School, related_name='students')
    person = models.ForeignKey(Person, related_name='studies_as')
    study_type = StudyTypeField(default = StudyType.ZS)
    start_date = models.DateField(auto_now_add=True)
        # Begining date of this relationship
        # Used to determine actual school in specified time
    end_date = models.DateField(default=None, editable=False)
        # Termination date of this relationship
        # Used to determine actual school in specified time
        # None/NULL when this is actual relationship
    expected_end_year = models.SmallIntegerField(default=None)
        # The year when full study would terimnate
        # Used to determine actual grade
    
    def __init__(self, *args, **kwargs):
        super(Student, self).__init__(self, *args, **kwargs)
        if self.expected_end_year == None :
            self.set_grade(1)
    
    def is_actual():
        return end_date == None
    
    def get_grade(self, act_date = None):
        """ Returns actual grade calculated from expected_end_year
            You can simulate another date by optional argument "act_date".
        """
        if act_date == None:
            act_date = date.now()
        act_year = Student.date_to_school_year(act_date)
        return act_year + self.study_type.max_grade - self.expected_end_year
    
    def set_grade(self, grade, act_date = None):
        """ Sets expected_end_year so that actual grade will change to given
            You can simulate another date by optional argument "act_date".
        """
        if act_date == None:
            act_date = date.now()
        act_year = Student.date_to_school_year(act_date)
        self.expected_end_year = act_year + self.study_type.max_grade - grade
        
    @staticmethod
    def date_to_school_year(date_):
        """ Returns a second year of a school year of given date. """
        if date_.month > 8:
            return date_.year+1
        else:
            return date_.year 
    

class Teacher(models.Model):
    """ An actual relationship between school and person teaching there.
        Also stores information about teached subjects.
    """
    school = models.ForeignKey(School, related_name='teachers')
    person = models.ForeignKey(Person, related_name='teaches_as')
    teaches_math = BooleanField()
    teaches_physics = BooleanField()
    teaches_informatics = BooleanField()
    


class StudyType(object):
    """ Set of informations about study type.
        Also defines all study types.
    """        
    ZS = StudyType('Základná škola', 'ZS', [None] + seq(1,10))
    SS = StudyType('Stredná škola', 'SS', [None] + seq(10,14))
    VS = StudyType('Vysoká škola', 'SS', [None] + seq(14,19))
    G8 = StudyType('8-ročné gymnázium', 'G8', [None] + seq(6,14))
    BL = StudyType('Bilingválne gymnázium', 'BL', [None, 10] + seq(10,14))
        
    def __init__(self, name, abbr, grade_to_absolute):
        self.name = name
        self.abbr = abbr
        self.grade_to_absolute = grade_to_absolute
        self.max_grade = len(grade_to_absolute)-1



class StudyTypeField(models.CharField):
    """ Converts StudyType-s between python and database."""
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        super(StudyTypeField, self).__init__(*args, **kwargs)
        
    def to_python(self, value):
        return getattr(StudyType, value)
        
    def get_prep_value(self, value):
        return value.abbr
'''
        
