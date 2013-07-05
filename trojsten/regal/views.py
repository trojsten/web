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

def show_table(request, caption, data_list, columns_func):
    columns = [x[0] for x in columns_func]
    data = []
    for item in data_list:
        data.append([x[1](item) for x in columns_func])
    return render_to_response('regal/show_table.html',
                              {'caption':caption, 'data':data, 'columns':columns},
                              context_instance=RequestContext(request))    

# shows table of adresses
# currently filter does nothing
def show_address(request, filter):
    address_list = Address.objects.filter()
    columns = [ 
        ('Street', lambda addr: addr.street),
        ('Number', lambda addr: addr.number),
        ('Town', lambda addr: addr.town),
        ('Country', lambda addr: addr.country),
    ]
    return show_table(request, 'Address', address_list, columns)
    
    


