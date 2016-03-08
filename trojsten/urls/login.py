from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from trojsten.regal.people.forms import TrojstenUserCreationForm, TrojstenUserChangeForm

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

# Override default forms in ksp_login
urlpatterns = patterns('ksp_login.views',
    url(r'^ucet/register/$', 'register', {'creation_form': TrojstenUserCreationForm, }, name='trojsten_register'),
    url(r'^ucet/$', 'settings', {'settings_form': TrojstenUserChangeForm, }, name='trojsten_account_settings'),
)

urlpatterns += patterns('',
    url(r'', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^ucet/', include('ksp_login.urls')),
)

# Include django debug toolbar views
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
