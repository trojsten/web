from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = patterns('',
    url(r'', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
