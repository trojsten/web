from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_notify_pattern
from contact_form.views import ContactFormView

from trojsten.regal.people.forms import TrojstenUserCreationForm, TrojstenUserChangeForm

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

# Override default forms in ksp_login
urlpatterns = patterns('ksp_login.views',
    url(r'^ucet/register/$', 'register', {'creation_form': TrojstenUserCreationForm, }, name='trojsten_register'),
    url(r'^ucet/$', 'settings', {'settings_form': TrojstenUserChangeForm, }, name='trojsten_account_settings'),
)

# Override default views in contact_form
urlpatterns += patterns('trojsten.views',
    url(r'^nahlasit-problem/$', ContactFormView.as_view(), name='contact_form'),
    url(r'^nahlasit-problem/sent/$', 'contact_form_sent_redirect',),
)

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'trojsten.views.home', name='home'),
    # url(r'^trojsten/', include('trojsten.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/',
    # include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ucet/', include('ksp_login.urls')),
    url(r'^nahlasit-problem/', include('contact_form.urls')),
    url(r'^wiki/notify/', get_notify_pattern()),
    url(r'^', include('favicon.urls')),
    url(r'^', get_wiki_pattern()),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
