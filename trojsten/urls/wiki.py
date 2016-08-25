from __future__ import absolute_import

from django.conf.urls import include, url
from django.contrib import admin


from django_nyt.urls import get_pattern as get_notify_pattern
from wiki.urls import get_pattern as get_wiki_pattern

from .common import urlpatterns as common_urlpatterns
from trojsten.views import CustomSearchView

urlpatterns = common_urlpatterns + [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^nahlasit-problem/', include('contact_form.urls')),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', include('favicon.urls')),
    url(r'^', get_wiki_pattern()),
    # Url for custom view of haystack elasticsearch
    url(r'^search/', CustomSearchView(), name='haystack_search'),
]
