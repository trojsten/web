import json

from django.shortcuts import render
from django.http import HttpResponseForbidden

from urllib2 import urlopen


def main(request):
    addr = request.META['REMOTE_ADDR']
    returned = json.loads(urlopen('http://ip-api.com/json/%s' % addr).read())
    if 'countryCode' in returned and returned['countryCode'] == 'SK':
        return HttpResponseForbidden()
    else:
        return render(request, 'plugin_prask_1_2_3/main.html', {})
