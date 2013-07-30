# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from regal.people.models import *
from regal.contests.models import *
import random, string, datetime

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

    for i in range(10):
        Address.objects.create(street=random_word(10), number=str(random.randint(1,20)), 
            town=random_word(5), country=random_word(5), postal_code=str(random.randint(1,10000)))
        Person.objects.create(name=random_word(5), surname=random_word(8), birth_date=datetime.date.today(), 
            email='a@b.cd', home_address=Address.objects.order_by('?')[0], correspondence_address=Address.objects.order_by('?')[0])
        School.objects.create(abbr=random_word(4), name=random_word(15), address=Address.objects.order_by('?')[0])

    if (not Competition.objects.all()):
        for x in ['KSP', 'KSP-T', 'OI', 'KMS']:
            c = Competition.objects.create(name=x)
            for i in range(random.randint(5,10)):
                y = Year.objects.create(competition=c, number=i+1, year=random.randint(1900,2100))
                for j in range(random.randint(0,5)):
                    r = Round.objects.create(year=y, number=j+1, end_time=datetime.datetime.fromtimestamp(random.randint(1,2**31)))
                    for k in range(random.randint(0,3)):
                        t = Task.objects.create(in_round=r, name=random_word(20), number=random.randint(1,6))


    return HttpResponse("entries generated")

