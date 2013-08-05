# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Simple middleware to allow different `urlconf`s depending on the hostname
(in preparation for serving ksp.sk, fks.sk, kms.sk, trojsten.sk from the
same instance)
"""

from django.conf import settings
from django.utils.cache import patch_vary_headers


class MultiHostnameMiddleware:

    def process_request(self, request):
        host = request.META['HTTP_HOST'].split(':')[0]
        try:
            request.urlconf = settings.HOST_MIDDLEWARE_URLCONF_MAP[host]
        except KeyError:
            pass  # use default urlconf from settings.ROOT_URLCONF

    def process_response(self, request, response):
        if getattr(request, 'urlconf', None):
            patch_vary_headers(response, ('Host',))
        return response
