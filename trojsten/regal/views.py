from django.shortcuts import render_to_response
from django.template import RequestContext

def print_word(request, word):
    return render_to_response('regal/print_word.html',
                              {'word':word},
                              context_instance=RequestContext(request))

