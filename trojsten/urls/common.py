from __future__ import absolute_import

import django
from contact_form.views import ContactFormView
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from ksp_login import views as login_views

import trojsten.views
from trojsten.people.forms import TrojstenUserCreationForm, TrojstenUserChangeForm

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

# Override default forms in ksp_login
urlpatterns = [
    url(r'^ucet/register/$', login_views.register, {'creation_form': TrojstenUserCreationForm},
        name='trojsten_register'),
    url(r'^ucet/$', login_views.settings, {'settings_form': TrojstenUserChangeForm},
        name='trojsten_account_settings'),
]

# Override default views in contact_form
urlpatterns += [
    url(r'^nahlasit-problem/$', ContactFormView.as_view(), name='contact_form'),
    url(r'^nahlasit-problem/sent/$', trojsten.views.contact_form_sent_redirect),
]

# Include django debug toolbar views
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
