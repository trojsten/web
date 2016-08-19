from __future__ import absolute_import

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<article_id>\d+)/$', views.transform_wiki_link, name='wiki_article')
]
