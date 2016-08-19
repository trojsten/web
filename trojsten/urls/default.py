from __future__ import absolute_import

from django.conf.urls import include, url
from django.contrib import admin

import news.urls
from django_nyt.urls import get_pattern as get_notify_pattern
from wiki.urls import get_pattern as get_wiki_pattern
import tips.urls

import trojsten.contests.views
import trojsten.contests.urls
import trojsten.results.urls
import trojsten.submit.urls
import trojsten.wiki_permalinks.urls
import trojsten.login.views

from .common import urlpatterns as common_urlpatterns

urlpatterns = common_urlpatterns + [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^ucet/remote_logout', trojsten.login.views.remote_logout, name='remote_account_logout'),
    url(r'^odovzdavanie/', include(trojsten.submit.urls)),
    url(r'^vysledky/', include(trojsten.results.urls)),
    url(r'^novinky/', include(news.urls)),
    url(r'^api/tips/', include(tips.urls, namespace='tips')),
    url(r'^ulohy/', include(trojsten.contests.urls)),
    url(r'^archiv/$', trojsten.contests.views.archive, {'path': '/archiv'},
        name='archive'),
    url(r'^akcie/', include('trojsten.events.urls')),
    url(r'^nahlasit-problem/', include('contact_form.urls')),
    url(r'^specialne/', include('trojsten.special.urls')),
    url(r'^komentare/', include('fluent_comments.urls')),
    url(r'^diskusie/', include('trojsten.threads.urls')),
    url(r'^$', trojsten.views.home_redirect),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', include('favicon.urls')),
    url(r'^permalinks/', include(trojsten.wiki_permalinks.urls)),
    url(r'^', get_wiki_pattern()),
]
