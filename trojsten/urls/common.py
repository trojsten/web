import django
import tips.urls
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from ksp_login import views as login_views

import trojsten.login.views
import trojsten.people.api_urls as people_api
import trojsten.views
from trojsten.contact_form.views import ContactFormView
from trojsten.people.forms import TrojstenUserChangeForm, TrojstenUserCreationForm
from trojsten.people.views import settings as settings_view

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

# Override default forms in ksp_login
urlpatterns = [
    url(
        r"^ucet/register/$",
        login_views.register,
        {"creation_form": TrojstenUserCreationForm},
        name="trojsten_register",
    ),
    url(
        r"^ucet/$",
        settings_view,
        {"settings_form": TrojstenUserChangeForm},
        name="trojsten_account_settings",
    ),
    url(r"^ucet/remote_logout", trojsten.login.views.remote_logout, name="remote_account_logout"),
]

# API
urlpatterns += [
    url(r"^api/tips/", include(tips.urls, namespace="tips")),
    url(r"^api/people/", include(people_api, namespace="people")),
    url(r"^api/notifications/", include("trojsten.notifications.urls")),
]

# Override default views in contact_form
urlpatterns += [
    url(r"^nahlasit-problem/$", ContactFormView.as_view(), name="contact_form"),
    url(r"^nahlasit-problem/sent/$", trojsten.views.contact_form_sent_redirect),
    url(r"^nahlasit-problem/", include("contact_form.urls")),
]

# Include django debug toolbar views
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(
            r"^media/(?P<path>.*)$",
            django.views.static.serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
        url(r"^__debug__/", include(debug_toolbar.urls)),
    ]
