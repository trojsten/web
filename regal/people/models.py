# -*- coding: utf-8 -*- 
from django.db import models
from datetime import date
from django.core.exceptions import ObjectDoesNotExist

##############################
#    PERSONAL INFORMATIONS   #
##############################


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

    class Meta:
        verbose_name = u'Address'
        verbose_name_plural = u'Addresses'



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
    # props <- related name to PersonProperty.property_type
    
    def actual_studies_as(self):
        """ Returns actual student relationship for this person
            Actual student is a student, who has NULL/None end_date
            Throws django.core.exceptions.MultipleObjectsReturned
            if there are multiple actual studnets.
        """
        try:
            r = self.studies_as.get(end_date = None)
            return r
        except ObjectDoesNotExist:
            return None
            
    def terminate_studies(self):
        """ Termintes all actual student relationships for this person
            Actual student is a student, who has NULL/None end_date
        """
        now = date.now()
        for act_student in self.studies_as.get(end_date = None):
            act_student.end_date = now
            if act_student.start_date == act_student.end_date:
                # act_student won't be interesting for the future
                act_student.delete()
                return
            act_student.save()
    
    def change_students_school(school, study_type, grade = 1):
        """ Terminates all actual students relationships
            and creates a new one from given school, study_type and grade
            Preffered way to create a new Student record.
            Returns created Student object.
        """
        self.terminate_studies()
        s = Student(
            school=school, person=self, study_type=study_type,
            start_date=date.now(), end_date=None)
        s.set_grade(grade)
        s.save()
        return s
    
    # TODO (sysel) function for properties dictionary
    
    def __unicode__(self):
        return self.name + " " + self.surname


class PersonPropertyCategory(models.Model):
    """ PersonPropertyTypes can be categorized for better UI organization. """
    abbr = models.CharField(max_length=8, primary_key=True)
        # Used instead of id
        # Note: primary_key=True implies null=False and unique=True
    name = models.CharField(max_length=128)
    # types <- related name to PersonPropertyType.category
    

class PersonPropertyType(models.Model):
    """ Describes one possible type additional person properties """
    abbr = models.CharField(max_length=16, primary_key=True)
        # Used instead of id
        # Note: primary_key=True implies null=False and unique=True
    name = models.CharField(max_length=128)
    validity_regex = models.TextField(null = False, default = "")
    single_per_user = models.BooleanField(default = True)
    category = models.ForeignKey(PersonPropertyCategory, related_name='types')
    user_editable = models.BooleanField(default = True)
    user_readable = models.BooleanField(default = True)
    # records <- related name to PersonProperty.property_type
    
class PersonProperty():
    """ Every adittional property of every person is stored as this. """
    # TODO (sysel) convert PersonProperty QuerySet to dictionary
    property_type = models.ForeignKey(PersonPropertyType, related_name='records')
    person = models.ForeignKey(PersonPropertyCategory, related_name='props')
    value = models.TextField(null = False, default = "")
    
        
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

    def get_town(self):
        return self.address.town
    

class StudyType(object):
    """ Set of informations about study type.
        Also defines all study types.
    """        
        
    def __init__(self, name, abbr, grade_to_absolute):
        self.name = name
        self.abbr = abbr
        self.grade_to_absolute = grade_to_absolute
        self.max_grade = len(grade_to_absolute)-1

# Didn't work inside StudyType
StudyType.ZS = StudyType('Základná škola', 'ZS', [None] + range(1,10))
StudyType.SS = StudyType('Stredná škola', 'SS', [None] + range(10,14))
StudyType.VS = StudyType('Vysoká škola', 'SS', [None] + range(14,19))
StudyType.G8 = StudyType('8-ročné gymnázium', 'G8', [None] + range(6,14))
StudyType.BL = StudyType('Bilingválne gymnázium', 'BL', [None, 10] + range(10,14))


class StudyTypeField(models.CharField):
    """ Converts StudyType-s between python and database."""
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        kwargs['null'] = False
        super(StudyTypeField, self).__init__(*args, **kwargs)
        
    def to_python(self, value):
        if isinstance(value, StudyType):
            return value
        return getattr(StudyType, value)
        
    def get_prep_value(self, value):
        return value.abbr


class Student(models.Model):
    """ A relationship between School and Person studying there.
        Holds and manges informations about relationship duration,
        study type, and student's grade.
        Should be able to give information about part of person's studies.
    """
    school = models.ForeignKey(School, related_name='students')
    person = models.ForeignKey(Person, related_name='studies_as')
    study_type = StudyTypeField(default = StudyType.ZS, null=False)
    start_date = models.DateField()
        # Begining date of this relationship
        # Used to determine actual school in specified time
    end_date = models.DateField()
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
    teaches_math = models.BooleanField()
    teaches_physics = models.BooleanField()
    teaches_informatics = models.BooleanField()
    


