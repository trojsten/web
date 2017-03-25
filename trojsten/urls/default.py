from __future__ import absolute_import

import news.urls
from django.conf.urls import include, url
from django.contrib import admin
from django_nyt.urls import get_pattern as get_notify_pattern
from wiki.urls import get_pattern as get_wiki_pattern

import trojsten.contests.urls
import trojsten.contests.views
import trojsten.login.views
import trojsten.people.views
import trojsten.results.urls
import trojsten.submit.urls

from .common import urlpatterns as common_urlpatterns

urlpatterns = common_urlpatterns + [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^ucet/additional_registration/?$',
        trojsten.people.views.additional_registration,
        name='additional_registration'),
    url(r'^odovzdavanie/', include(trojsten.submit.urls)),
    url(r'^vysledky/', include(trojsten.results.urls)),
    url(r'^novinky/', include(news.urls)),
    url(r'^ulohy/', include(trojsten.contests.urls)),
    url(r'^archiv/$', trojsten.contests.views.archive, {'path': '/archiv'},
        name='archive'),
    url(r'^akcie/', include('trojsten.events.urls')),
    url(r'^specialne/', include('trojsten.special.urls')),
    url(r'^komentare/', include('fluent_comments.urls')),
    url(r'^diskusie/', include('trojsten.threads.urls')),
    url(r'^$', trojsten.views.home_redirect),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', include('favicon.urls')),
    url(r'^', get_wiki_pattern()),
]
