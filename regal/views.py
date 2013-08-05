# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from regal.people.models import *
from regal.contests.models import *
from regal.problems.models import *
import random
import string
import datetime


def random_word(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def dashboard(request):
    context = {

    }

    return render_to_response('regal/dashboard.html',
                              context,
                              context_instance=RequestContext(request))


def generate(request):
    ''' temporary page, just for debugging purpose
        generates some random entries in tables
    '''
    persons = []

    for i in range(10):
        Address.objects.create(
            street=random_word(10), number=str(random.randint(1, 20)),
            town=random_word(5), country=random_word(5), postal_code=str(random.randint(1, 10000)))
        persons.append(
            Person.objects.create(
                name=random_word(5), surname=random_word(8), birth_date=datetime.date.today(),
                email='a@b.cd', home_address=Address.objects.order_by('?')[0],
                correspondence_address=Address.objects.order_by('?')[0]))
        School.objects.create(abbr=random_word(4), name=random_word(
            15), address=Address.objects.order_by('?')[0])

    submit_types = ['prax', 'teoria']

    if (not Competition.objects.all()):
        for x in ['KSP', 'KSP-T', 'OI', 'KMS']:
            c = Competition.objects.create(name=x)
            for i in range(random.randint(4, 7)):
                s = Series.objects.create(
                    competition=c, name=random_word(10), year=random.randint(1, 30),
                    start_date=datetime.date.fromtimestamp(random.randint(1, 2 ** 31)))
                for j in range(random.randint(0, 3)):
                    r = Round.objects.create(series=s, number=j + 1,
                                             end_time=datetime.datetime.fromtimestamp(random.randint(1, 2 ** 31)))
                    for k in range(random.randint(0, 3)):
                        t = Task.objects.create(
                            in_round=r, name=random_word(6), number=k + 1)
                        for l in range(random.randint(1, 3)):
                            Evaluation.objects.create(
                                task=t, person=persons[
                                    random.randint(0, len(persons) - 1)],
                                points=str(random.randint(0, 10)), submit=random_word(10),
                                submit_type=submit_types[random.randint(0, 1)])

    return HttpResponse("entries generated")
