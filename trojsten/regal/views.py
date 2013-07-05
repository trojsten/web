# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

from trojsten.regal.models import Address, Person, School

##############################
# JUST AN INCOMPLETE CONCEPT #
##############################

# test
def print_word(request, word):
    return render_to_response('regal/print_word.html',
                              {'word':word},
                              context_instance=RequestContext(request))

# creates and shows a table
#   caption - name of table
#   columns_func - list of pair (<column name>, lambda <data row>: value)
#   data_list - list od <data row>

def generate_table(request, caption, data_list, columns_func):
    columns = [x[0] for x in columns_func]
    data = []
    for item in data_list:
        data.append([x[1](item) for x in columns_func])
    return render_to_response('regal/show_table.html',
                              {'caption':caption, 'data':data, 'columns':columns},
                              context_instance=RequestContext(request))    

# shows table of adresses
# filter does nothing  currently

def show_addresses(request, filter):
    address_list = Address.objects.filter()
    columns = [ 
        (u'Ulica', lambda addr: addr.street),
        (u'Číslo', lambda addr: addr.number),
        (u'Mesto', lambda addr: addr.town),
        (u'Štát', lambda addr: addr.country),
    ]
    return generate_table(request, u'Adresy', address_list, columns)
    
    
# filter does nothing  currently

def show_persons(request, filter):
    person_list = Person.objects.filter()
    columns = [ 
        (u'Id', lambda p: p.id),
        (u'Meno', lambda p: p.name),
        (u'Priezvisko', lambda p: p.surname),
    ]
    return generate_table(request, u'Osoby', person_list, columns)

# filter does nothing currently

def show_schools(request, filter):
    school_list = School.objects.filter()
    columns = [ 
        (u'Skatka', lambda s: s.abbr),
        (u'Celé meno', lambda s: s.name),
    ]
    return generate_table(request, u'Školy', school_list, columns)

def show_home(request):
    tables = [
        (u'Adresy','addresses',u'Zoznam adries'),
        (u'Osoby','persons',u'Všetci ľudia'),
        (u'Školy','schools',u'Zoznam škôl'),
    ]

    caption = 'Rhaegal'
    return render_to_response('regal/home.html',
                              {'caption':caption, 'tables':tables},
                              context_instance=RequestContext(request))
    
