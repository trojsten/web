from django.db import models

##############################
# JUST AN INCOMPLETE CONCEPT #
##############################

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
    id = models.IntegerField(primary_key=True)
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

        
       
