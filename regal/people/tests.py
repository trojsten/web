# -*- coding: utf-8 -*-

from django.test import TestCase
from models import *
from datetime import date

def initPersons():
    Person.objects.create(
        name='Jožko',
        surname='Mrkvička',
        email='jozko@mrkvicka.sk',
        birth_date=date(1996,1,1))
    Person.objects.create(
        name='Ferko',
        surname='Machuľa',
        email='ferko@mrkvicka.sk',
        birth_date=date(1995,12,31))
        
class PersonPropsTest(TestCase):
    def setUp(self):
        initPersons()
        cat = PersonPropertyCategory(name='Test')
        cat.save()
        types = []
        types.append(PersonPropertyType(name="A", category=cat))
        types.append(PersonPropertyType(name="B", category=cat))
        types.append(PersonPropertyType(name="M", multi=True, category=cat))
        for x in types:
            x.save()
        
    def test_singleprop_values(self):
        # read from database
        personX = Person.objects.get(id=1) # set person
        personY = Person.objects.get(id=1) # test person
        A = PersonPropertyType.objects.get(name='A')
        B = PersonPropertyType.objects.get(name='B')
        # clear data
        personX.props.all().delete()
        # set & test
        personX.props[A].set_value('42')
        personX.props[B].set_value('47')
        self.assertEqual(personY.props[A].value(), '42')
        self.assertEqual(personY.props[B].value(), '47')
        personX.props[A].set_value('89')
        self.assertEqual(personY.props[A].value(), '89')
        
    def test_multiprop_values(self):
        # read from database
        personX = Person.objects.get(id=1) # set person
        personY = Person.objects.get(id=1) # test person
        M = PersonPropertyType.objects.get(name='M')
        # clear data
        personX.props.all().delete()
        # set & test
        personX.props[M].add_value('poo')
        personX.props[M].add_value('foo')
        self.assertEqual(personY.props[M].count(), 2)
        self.assertEqual(personY.props[M].values(), set(['poo','foo']))
        personX.props[M].delete_value('foo')
        self.assertEqual(personY.props[M].count(), 1)
        
    def test_props_dict(self):
        # read from database
        personX = Person.objects.get(id=1) # set person
        personY = Person.objects.get(id=1) # test person
        M = PersonPropertyType.objects.get(name='M')
        A = PersonPropertyType.objects.get(name='A')
        # clear data
        personX.props.all().delete()
        # set & test
        personX.props[M].add_value('poo')
        personX.props[A].set_value('42')
        pdict = personX.props.create_dict()
        self.assertEqual(pdict[M], set(['poo']))
        self.assertEqual(pdict[A], '42')
        pdict[A] = '47'
        pdict[M].add('foo')
        pdict.save()
        self.assertEqual(personY.props[M].values(), set(['poo','foo']))
        self.assertEqual(personY.props[A].value(), '47')
        del pdict[A]
        pdict[M].remove('poo')
        self.assertEqual(personY.props.count(), 3)
        pdict.save()
        self.assertEqual(personY.props.count(), 1)
        
    def test_multiple_persons(self):
        # read from database
        person1 = Person.objects.get(id=1)
        person2 = Person.objects.get(id=2)
        A = PersonPropertyType.objects.get(name='A')
        # clear data
        person1.props.all().delete()
        person2.props.all().delete()
        # set & test
        person1.props[A].set_value('42')
        person2.props[A].set_value('47')
        self.assertEqual(person1.props[A].value(), '42')
        self.assertEqual(person2.props[A].value(), '47')
        
        
class StudentTest(TestCase):
    def setUp(self):
        initPersons()
        School.objects.create(
            name="Gymnázium Michala Anderleho v Lučenci",
            abbr="GŽaba")
        
    def test_actual_study(self):
        # read from database
        person = Person.objects.get(id=1) 
        school = School.objects.get(abbr='GŽaba') 
        # clear data
        person.studies_as.all().delete()
        # set & test
        self.assertEqual(person.study(), None)
        person.change_study(school, StudyType.ZS)
        self.assertEqual(person.study().study_type, StudyType.ZS)
        self.assertEqual(person.study().school, school)
        person.change_study(school, StudyType.SS)
        self.assertEqual(person.study().study_type, StudyType.SS)
        person.terminate_studies()
        self.assertEqual(person.study(), None)

    def test_grades(self):
        person = Person.objects.get(id=1) 
        school = School.objects.get(abbr='GŽaba') 
        # clear data
        person.studies_as.all().delete()
        # set & test
        person.change_study(school, StudyType.ZS, 8)
        self.assertEqual(person.study().get_grade(), 8)
        self.assertEqual(person.study().get_absolute_grade(), 8)
        person.change_study(school, StudyType.BL) # bilingval, first grade
        student = person.study()
        self.assertEqual(student.get_absolute_grade(), 10)
        student.set_grade(2) # bilingval, second grade
        self.assertEqual(student.get_absolute_grade(), 10)
        student.set_grade(3) # bilingval, third grade
        self.assertEqual(student.get_absolute_grade(), 11)

