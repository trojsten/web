# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

def dashboard(request):
    context = {

    }

    return render_to_response('regal/dashboard.html',
                              context,
                              context_instance=RequestContext(request))

