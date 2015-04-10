# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.shortcuts import render
from django.http import HttpResponse

from urllib2 import urlopen


def main(request):
    addr = request.META['REMOTE_ADDR']
    returned = json.loads(urlopen('http://ip-api.com/json/%s' % addr).read())
    if 'countryCode' in returned and returned['countryCode'] == 'SK':
        return HttpResponse("Pre riešiteľov Prasku zo Slovenska je táto stránka neprístupná.")
    else:
        return render(request, 'plugin_prask_1_2_3/main.html', {})
