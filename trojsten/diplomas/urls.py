# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.view_diplomas, {'path': '/diplomy_tutorial'}, name='view_diplomas')
]
