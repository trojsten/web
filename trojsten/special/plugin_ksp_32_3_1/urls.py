# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.defaults import page_not_found

from .views import index, level, levels, solution, submit_status

urlpatterns = [
    url(r'^$', index),
    url(r'^levels$', levels),
    url(r'^levels/s(?P<sid>\d+)l(?P<lid>\d+)$', level),
    url(r'^solutions/s(?P<sid>\d+)l(?P<lid>\d+)$', solution),
    url(r'^submits/(?P<pk>\d+)$', submit_status),
    url(r'^.*$', page_not_found),
]
