import news.urls
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from social_django.views import auth as social_auth

import trojsten.contests.urls
import trojsten.contests.views
import trojsten.diplomas.urls
import trojsten.people.views
import trojsten.results.urls
import trojsten.submit.urls
import trojsten.submit.views

from .common import urlpatterns as common_urlpatterns

login_redirect = []
if not settings.TESTING:
    login_redirect = [url(r"^ucet/login/$", social_auth, {"backend": "trojsten"})]

urlpatterns = (
    common_urlpatterns
    + login_redirect
    + [
        url(r"^admin/", admin.site.urls),
        url(r"^ucet/", include("ksp_login.urls")),
        url(
            r"^ucet/additional_registration/?$",
            trojsten.people.views.additional_registration,
            name="additional_registration",
        ),
        url(r"^odovzdavanie/", include(trojsten.submit.urls)),
        url(r"^vysledky/", include(trojsten.results.urls)),
        url(r"^diplomy/", include(trojsten.diplomas.urls)),
        url(r"^novinky/", include(news.urls)),
        url(r"^ulohy/", include(trojsten.contests.urls)),
        url(r"^archiv/$", trojsten.contests.views.archive, {"path": "/archiv"}, name="archive"),
        url(r"^nastenka/$", trojsten.contests.views.dashboard, name="dashboard"),
        url(
            r"^mojeulohy/$",
            trojsten.submit.views.all_submits_description_page,
            name="all_submits_description_page",
        ),
        url(
            r"^mojesubmity/$",
            trojsten.submit.views.all_submits_source_page,
            name="all_submits_source_page",
        ),
        url(r"^akcie/", include("trojsten.events.urls")),
        url(r"^specialne/", include("trojsten.special.urls")),
        url(r"^komentare/", include("fluent_comments.urls")),
        url(r"^diskusie/", include("trojsten.threads.urls")),
        url(r"^$", trojsten.views.home_redirect),
        url(r"^wiki/notify/", include("django_nyt.urls")),
        url(r"^", include("favicon.urls")),
        url(r"^", include("wiki.urls")),
    ]
)
