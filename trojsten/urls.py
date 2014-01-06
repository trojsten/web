from django.conf.urls import patterns, include, url
from django.contrib import admin
import trojsten.submit.urls

admin.autodiscover()

from wiki.urls import get_pattern as get_wiki_pattern
from django_notify.urls import get_pattern as get_notify_pattern

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trojsten.views.home', name='home'),
    # url(r'^trojsten/', include('trojsten.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/',
    # include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^submit/', include(trojsten.submit.urls)),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', get_wiki_pattern()),
)
