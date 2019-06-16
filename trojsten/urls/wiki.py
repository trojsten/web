from __future__ import absolute_import

from django.conf.urls import include, url
from django.contrib import admin

from trojsten.views import CustomSearchView

from .common import urlpatterns as common_urlpatterns

urlpatterns = common_urlpatterns + [
    url(r"^admin/", admin.site.urls),
    url(r"^ucet/", include("ksp_login.urls")),
    url(r"^nahlasit-problem/", include("contact_form.urls")),
    url(r"^wiki/notify/", include("django_nyt.urls")),
    url(r"^search/", CustomSearchView(), name="haystack_search"),
    url(r"^", include("favicon.urls")),
    url(r"^", include("wiki.urls")),
]
