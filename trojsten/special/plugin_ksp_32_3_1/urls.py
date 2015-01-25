# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, handler404

from .views import *


urlpatterns = patterns(
    '',
    url(r'^/$', index),
    url(r'^levels/$', levels),
    url(r'^levels/s(?P<sid>\d+)l(?P<lid>\d+)/$', level),
    url(r'^submits/(?P<pk>\d+)/$', submit_status),
    url(r'^.*$', handler404),
)
