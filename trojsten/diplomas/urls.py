# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.view_diplomas, name='view_diplomas'),
    url(r'^(?P<diploma_id>(\d+))/preview/$', views.diploma_preview, name='diploma_preview'),
    url(r'^(?P<diploma_id>(\d+))/sources/$', views.diploma_sources, name='diploma_sources'),
    url(r'^sources/(?P<source_class>([\w]+))/$', views.source_request, name='source_request'),
    url(r'^tutorial/', views.view_tutorial, {'path': '/diplomy_tutorial'}, name='diploma_tutorial')
]
