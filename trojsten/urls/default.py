from __future__ import absolute_import

from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_notify_pattern

from .common import *

import trojsten.archive.views
import trojsten.submit.urls
import trojsten.results.urls
import trojsten.news.urls
import trojsten.task_statements.urls
import trojsten.views


urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^odovzdavanie/', include(trojsten.submit.urls)),
    url(r'^vysledky/', include(trojsten.results.urls)),
    url(r'^novinky/', include(trojsten.news.urls)),
    url(r'^ulohy/', include(trojsten.task_statements.urls)),
    url(r'^archiv/$', trojsten.archive.views.archive, {'path': '/archiv',},
        name='archive'),
    url(r'^akcie/', include('trojsten.events.urls')),
    url(r'^nahlasit-problem/', include('contact_form.urls')),
    url(r'^specialne/', include('trojsten.special.urls')),
    url(r'^komentare/', include('fluent_comments.urls')),
    url(r'^diskusie/', include('trojsten.threads.urls')),
    url(r'^$', trojsten.views.home_redirect),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', include('favicon.urls')),
    url(r'^', get_wiki_pattern()),
]
