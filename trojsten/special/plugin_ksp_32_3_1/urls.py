# -*- coding: utf-8 -*-

from django.conf.urls import handler404, url

from .views import *

urlpatterns =[
    url(r'^$', index),
    url(r'^levels$', levels),
    url(r'^levels/s(?P<sid>\d+)l(?P<lid>\d+)$', level),
    url(r'^solutions/s(?P<sid>\d+)l(?P<lid>\d+)$', solution),
    url(r'^submits/(?P<pk>\d+)$', submit_status),
    url(r'^.*$', handler404),
]
